Complete Updated Files for STK Czechr Integration

# 1. const.py - Replace entire file content
DOMAIN = "stk_czechr"

# Config keys
CONF_NAME = "name"
CONF_VIN = "vin"

# Platform names
PLATFORM_SENSOR = "sensor"

# Error messages
ERROR_INVALID_VIN = "Invalid VIN provided"
ERROR_VIN_EXISTS = "This VIN is already configured"
ERROR_API_TIMEOUT = "API request timed out"
ERROR_API_CONNECTION = "Could not connect to API"

# Update frequency
DEFAULT_UPDATE_INTERVAL = 86400  # 24 hours in seconds
API_TIMEOUT = 10  # seconds

# Sensor types with their translations
SENSOR_TYPES = {
    "last_check_date": {
        "name": "Datum poslední kontroly",
        "icon": "mdi:calendar-check",
        "device_class": "date",
    },
    "valid_until": {
        "name": "Platnost STK",
        "icon": "mdi:calendar-clock",
        "device_class": "date",
    },
    "days_remaining": {
        "name": "Dní do konce platnosti",
        "icon": "mdi:timer-sand",
        "device_class": "duration",
        "unit_of_measurement": "days",
    },
    "status": {
        "name": "Stav STK",
        "icon": "mdi:car-wrench",
    }
}

# API endpoints
API_ENDPOINT = "https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo"

class STKStatus:
    VALID = "valid"
    EXPIRED = "expired"
    WARNING = "warning"  # Less than 30 days remaining
    UNKNOWN = "unknown"
