# geohealthai/backend/database/mysql_db.py

# geohealthai/backend/database/mysql_db.py

"""
MySQL + Cache Helper for GeoHealthAI
------------------------------------
Stores:
    ✓ User requests (text, nlp, ml, recs)
    ✓ Environment caches: pollution / climate / NDVI env_risk

This file is fully synchronous to match your engines.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Float
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("MYSQL_URL")
engine = None
metadata = MetaData()


# -------------------------------------------------------
# TABLE 1: requests (your old table, kept intact)
# -------------------------------------------------------
requests_table = Table(
    "requests",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime, nullable=False),
    Column("user_text", Text),
    Column("location", Text),
    Column("nlp_features", LONGTEXT),
    Column("ml_predictions", LONGTEXT),
    Column("recommendations", LONGTEXT),
    Column("client_ip", String(100)),
)


# -------------------------------------------------------
# TABLE 2: environment_cache (for pollution/climate/env)
# -------------------------------------------------------
environment_cache = Table(
    "environment_cache",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("key", String(200), index=True, nullable=False),
    Column("source", String(50)),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("data_json", Text),
    Column("created_at", DateTime, nullable=False),
)


# -------------------------------------------------------
# Initialize MySQL
# -------------------------------------------------------
def init_mysql():
    global engine
    if not DATABASE_URL:
        logger.warning("MYSQL_URL not set; MySQL disabled.")
        return

    try:
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            future=True,
        )
        metadata.create_all(engine)
        logger.info("MySQL connected and ALL tables ensured (requests + env_cache).")
    except SQLAlchemyError as e:
        logger.exception("MySQL init failed: %s", e)
        engine = None


# -------------------------------------------------------
# Save analyze request
# -------------------------------------------------------
def save_request(
    user_text: str,
    location_dict: Optional[Dict[str, Any]],
    nlp_features: Optional[Dict[str, Any]],
    ml_predictions: Optional[Dict[str, Any]],
    recommendations: Optional[List[str]],
    client_ip: Optional[str] = None,
):
    if engine is None:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                insert(requests_table).values(
                    timestamp=datetime.utcnow(),
                    user_text=user_text,
                    location=json.dumps(location_dict) if location_dict else None,
                    nlp_features=json.dumps(nlp_features) if nlp_features else None,
                    ml_predictions=json.dumps(ml_predictions) if ml_predictions else None,
                    recommendations=json.dumps(recommendations) if recommendations else None,
                    client_ip=client_ip,
                )
            )
        logger.info("Saved request to MySQL.")
    except SQLAlchemyError as e:
        logger.exception("save_request failed: %s", e)


# -------------------------------------------------------
# Internal cache helpers
# -------------------------------------------------------
def _latest_row(key: str):
    if engine is None:
        return None
    with engine.connect() as conn:
        stmt = (
            select(environment_cache)
            .where(environment_cache.c.key == key)
            .order_by(environment_cache.c.created_at.desc())
            .limit(1)
        )
        return conn.execute(stmt).first()


def _set_cache(key: str, source: str, lat: float, lon: float, data: dict):
    if engine is None:
        return
    with engine.begin() as conn:
        conn.execute(
            insert(environment_cache).values(
                key=key,
                source=source,
                latitude=lat,
                longitude=lon,
                data_json=json.dumps(data),
                created_at=datetime.utcnow(),
            )
        )


# -------------------------------------------------------
# POLLUTION CACHE
# -------------------------------------------------------
def get_cached_pollution(city: str, state: str, hour_key: str):
    key = f"pollution:{city.lower()}:{state.lower()}:{hour_key}"
    row = _latest_row(key)
    if not row:
        return None
    try:
        return float(json.loads(row.data_json)["pollution_risk"])
    except:
        return None


def set_cached_pollution(city: str, state: str, hour_key: str, risk: float, pm25=None):
    key = f"pollution:{city.lower()}:{state.lower()}:{hour_key}"
    _set_cache(key, "openaq", None, None, {"pollution_risk": float(risk), "pm25": pm25})


# -------------------------------------------------------
# CLIMATE CACHE
# -------------------------------------------------------
def get_cached_climate(lat: float, lon: float, hour_key: str):
    key = f"climate:{lat:.4f}:{lon:.4f}:{hour_key}"
    row = _latest_row(key)
    if not row:
        return None
    try:
        return float(json.loads(row.data_json)["climate_risk"])
    except:
        return None


def set_cached_climate(lat: float, lon: float, hour_key: str, risk: float, temp=None, humidity=None):
    key = f"climate:{lat:.4f}:{lon:.4f}:{hour_key}"
    _set_cache(
        key, "openmeteo", lat, lon,
        {"climate_risk": float(risk), "temp": temp, "humidity": humidity}
    )


# -------------------------------------------------------
# ENVIRONMENT (NDVI) CACHE
# -------------------------------------------------------
def get_cached_env(city: str, state: str):
    key = f"env:{city.lower()}:{state.lower()}"
    row = _latest_row(key)
    if not row:
        return None
    try:
        return float(json.loads(row.data_json)["env_risk"])
    except:
        return None


def set_cached_env(city: str, state: str, risk: float):
    key = f"env:{city.lower()}:{state.lower()}"
    _set_cache(key, "ndvi", None, None, {"env_risk": float(risk)})


"""
Simple MySQL helper using SQLAlchemy to persist user requests, NLP features,
ML predictions and recommendations for future training/analytics.

Usage:
    from backend.database import mysql_db
    mysql_db.init_mysql()
    mysql_db.save_request(...)


import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Text, DateTime
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()  # loads backend/.env if present

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("MYSQL_URL", None)

engine: Optional[Engine] = None
metadata = MetaData()

# Table: requests -> store each analyze request & results
requests_table = Table(
    "requests",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime, nullable=False),  # NO DEFAULT
    Column("user_text", Text, nullable=True),
    Column("location", Text, nullable=True),
    Column("nlp_features", LONGTEXT, nullable=True),
    Column("ml_predictions", LONGTEXT, nullable=True),
    Column("recommendations", LONGTEXT, nullable=True),
    Column("client_ip", String(100), nullable=True),
)



def init_mysql():
    global engine
    if not DATABASE_URL:
        logger.warning("MYSQL_URL not set; MySQL storage disabled.")
        return
    try:
        # create engine with basic pool
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            future=True,
        )
        metadata.create_all(engine)
        logger.info("MySQL connected and tables ensured.")
    except SQLAlchemyError as e:
        logger.exception("Failed to init MySQL engine: %s", e)
        engine = None


def save_request(
    user_text: str,
    location_dict: Optional[Dict[str, Any]],
    nlp_features: Optional[Dict[str, Any]],
    ml_predictions: Optional[Dict[str, Any]],
    recommendations: Optional[List[str]],
    client_ip: Optional[str] = None,
):
    "
    Persist one analyze request and pipeline outputs into MySQL.
    This is safe to call even if MySQL is not configured (it becomes no-op).
    "
    if engine is None:
        logger.debug("MySQL engine not initialized; skipping save_request.")
        return
    try:
        conn = engine.connect()
        ins = requests_table.insert().values(
            timestamp=datetime.utcnow(),   # ADD THIS LINE
            user_text=user_text,
            location=json.dumps(location_dict) if location_dict else None,
            nlp_features=json.dumps(nlp_features) if nlp_features else None,
            ml_predictions=json.dumps(ml_predictions) if ml_predictions else None,
            recommendations=json.dumps(recommendations) if recommendations else None,
            client_ip=client_ip,
        )
        conn.execute(ins)
        conn.commit()
        conn.close()
        logger.info("Saved analyze request to MySQL.")
    except SQLAlchemyError as e:
        logger.exception("Failed to save request to MySQL: %s", e)"""
