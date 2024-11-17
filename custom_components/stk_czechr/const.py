# Custom component domain
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
    # Core STK sensors
    "valid_until": {
        "name": "Platnost STK",
        "icon": "mdi:calendar-clock",
        "device_class": "date",
        "api_field": "PravidelnaTechnickaProhlidkaDo",
    },
    "days_remaining": {
        "name": "Dní do konce platnosti",
        "icon": "mdi:timer-sand",
        "device_class": "duration",
        "unit_of_measurement": "days",
        "enabled_by_default": True,
    },
    "status": {
        "name": "Stav STK",
        "icon": "mdi:car-wrench",
        "enabled_by_default": True,
    },
    
    # Vehicle information
    "first_registration": {
        "name": "Datum první registrace",
        "icon": "mdi:calendar",
        "device_class": "date",
        "api_field": "DatumPrvniRegistrace",
    },
    "brand": {
        "name": "Značka",
        "icon": "mdi:car",
        "api_field": "TovarniZnacka",
    },
    "model": {
        "name": "Model",
        "icon": "mdi:car-side",
        "api_field": "ObchodniOznaceni",
    },
    "color": {
        "name": "Barva",
        "icon": "mdi:palette",
        "api_field": "VozidloKaroserieBarva",
    },
    
    # Technical parameters
    "engine_power": {
        "name": "Výkon motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "kW",
        "device_class": "power",
        "api_field": "MotorMaxVykon",
    },
    "engine_displacement": {
        "name": "Objem motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "cm³",
        "api_field": "MotorZdvihObjem",
    },
    "fuel_type": {
        "name": "Palivo",
        "icon": "mdi:gas-station",
        "api_field": "Palivo",
    },
    "max_speed": {
        "name": "Maximální rychlost",
        "icon": "mdi:speedometer",
        "unit_of_measurement": "km/h",
        "api_field": "NejvyssiRychlost",
    },
    
    # Consumption and emissions
    "fuel_consumption_combined": {
        "name": "Kombinovaná spotřeba",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "api_field": "SpotrebaNa100Km120",
    },
    "co2_emissions": {
        "name": "Emise CO2",
        "icon": "mdi:molecule-co2",
        "unit_of_measurement": "g/km",
        "api_field": "EmiseCO2",
    },
}

# API endpoints
API_ENDPOINT = "https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo"

class STKStatus:
    VALID = "valid"
    EXPIRED = "expired"
    WARNING = "warning"  # Less than 30 days remaining
    UNKNOWN = "unknown"
