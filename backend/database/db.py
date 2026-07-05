from pathlib import Path
import sqlite3
import threading
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "geohealth_cache.db"

_lock = threading.Lock()
_conn: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    """
    Returns a singleton SQLite connection (thread-safe initialization).
    """
    global _conn
    if _conn is None:
        with _lock:
            if _conn is None:
                _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                _conn.row_factory = sqlite3.Row
                _init_db(_conn)
    return _conn


def _init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    # Pollution cache: one entry per (city, state, hour_key)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pollution_cache (
            city TEXT NOT NULL,
            state TEXT,
            hour_key TEXT NOT NULL,
            pollution_risk REAL NOT NULL,
            PRIMARY KEY(city, state, hour_key)
        )
        """
    )

    # Climate cache: one entry per (lat, lon, hour_key)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS climate_cache (
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            hour_key TEXT NOT NULL,
            climate_risk REAL NOT NULL,
            PRIMARY KEY(latitude, longitude, hour_key)
        )
        """
    )

    # Environment cache: one entry per (city, state)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS env_cache (
            city TEXT NOT NULL,
            state TEXT,
            env_risk REAL NOT NULL,
            PRIMARY KEY(city, state)
        )
        """
    )

    conn.commit()


# ----- Pollution cache helpers -----

def get_cached_pollution(city: str, state: str, hour_key: str) -> Optional[float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT pollution_risk FROM pollution_cache WHERE city=? AND state=? AND hour_key=?",
        (city.lower(), state.lower(), hour_key),
    )
    row = cur.fetchone()
    return float(row["pollution_risk"]) if row else None


def set_cached_pollution(city: str, state: str, hour_key: str, pollution_risk: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO pollution_cache (city, state, hour_key, pollution_risk)
        VALUES (?, ?, ?, ?)
        """,
        (city.lower(), state.lower(), hour_key, float(pollution_risk)),
    )
    conn.commit()


# ----- Climate cache helpers -----

def get_cached_climate(latitude: float, longitude: float, hour_key: str) -> Optional[float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT climate_risk FROM climate_cache
        WHERE latitude=? AND longitude=? AND hour_key=?
        """,
        (latitude, longitude, hour_key),
    )
    row = cur.fetchone()
    return float(row["climate_risk"]) if row else None


def set_cached_climate(latitude: float, longitude: float, hour_key: str, climate_risk: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO climate_cache (latitude, longitude, hour_key, climate_risk)
        VALUES (?, ?, ?, ?)
        """,
        (latitude, longitude, hour_key, float(climate_risk)),
    )
    conn.commit()


# ----- Environment cache helpers -----

def get_cached_env(city: str, state: str) -> Optional[float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT env_risk FROM env_cache WHERE city=? AND state=?",
        (city.lower(), state.lower()),
    )
    row = cur.fetchone()
    return float(row["env_risk"]) if row else None


def set_cached_env(city: str, state: str, env_risk: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO env_cache (city, state, env_risk)
        VALUES (?, ?, ?)
        """,
        (city.lower(), state.lower(), float(env_risk)),
    )
    conn.commit()
