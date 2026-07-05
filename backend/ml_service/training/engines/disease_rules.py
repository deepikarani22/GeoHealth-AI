# Medical + environmental rule definitions

DISEASE_ENV_RULES = {
    "Asthma": {
        "pm25": 35,
        "pm10": 50,
        "no2": 40,
        "humidity_min": 30,
        "humidity_max": 80,
        "temp_min": 5,
        "temp_max": 40
    },
    "COPD": {
        "pm25": 25,
        "pm10": 40,
        "no2": 30
    },
    "HeatStress": {
        "temp_min": 38,
        "humidity_min": 60
    },
    "Hypothermia": {
        "temp_max": 5
    },
    "AllergicRhinitis": {
        "pollen_index": 3,
        "ndvi_min": 0.3
    },
    "Dengue": {
        "temp_min": 25,
        "humidity_min": 60,
        "stagnant_water": True
    }
}
