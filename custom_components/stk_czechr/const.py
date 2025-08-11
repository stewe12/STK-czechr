# Custom component domain
DOMAIN = "stk_czechr"

# Config keys
CONF_NAME = "name"
CONF_VIN = "vin"
CONF_API_KEY = "api_key"

# Platform names
PLATFORM_SENSOR = "sensor"

# Error messages
ERROR_INVALID_VIN = "Invalid VIN provided"
ERROR_VIN_EXISTS = "This VIN is already configured"
ERROR_API_FAILED = "API request failed"
ERROR_NO_DATA_FOUND = "No vehicle data found"
ERROR_RATE_LIMITED = "Rate limited - try again later"
ERROR_API_KEY_MISSING = "API key is required for dataovozidlech.cz"

# Update frequency (1 minute in seconds for rate limiting)
DEFAULT_UPDATE_INTERVAL = 60  # 1 minute
API_TIMEOUT = 30  # seconds

# API endpoints
API_BASE_URL = "https://api.dataovozidlech.cz/api/vehicletechnicaldata/v2"
API_REGISTRATION_URL = "https://dataovozidlech.cz/registraceApi"
API_DOCUMENTATION_URL = "https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf"

# Sensor types with their translations
SENSOR_TYPES = {
    # Core STK sensors - enabled by default
    "valid_until": {
        "name": "Platnost STK",
        "icon": "mdi:calendar-clock",
        "device_class": "date",
        "enabled_by_default": True,
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
    
    # Vehicle identification - enabled by default
    "brand": {
        "name": "Značka",
        "icon": "mdi:car",
        "enabled_by_default": True,
    },
    "model": {
        "name": "Model",
        "icon": "mdi:car-side",
        "enabled_by_default": True,
    },
    "vin": {
        "name": "VIN",
        "icon": "mdi:identifier",
        "enabled_by_default": True,
    },
    
    # Physical characteristics - enabled by default
    "color": {
        "name": "Barva",
        "icon": "mdi:palette",
        "enabled_by_default": True,
    },
    "weight": {
        "name": "Provozní hmotnost",
        "icon": "mdi:weight",
        "unit_of_measurement": "kg",
        "enabled_by_default": True,
    },
    
    # Dimensions - enabled by default
    "length": {
        "name": "Délka",
        "icon": "mdi:arrow-expand-horizontal",
        "unit_of_measurement": "mm",
        "enabled_by_default": True,
    },
    "width": {
        "name": "Šířka",
        "icon": "mdi:arrow-expand-horizontal",
        "unit_of_measurement": "mm",
        "enabled_by_default": True,
    },
    "height": {
        "name": "Výška",
        "icon": "mdi:arrow-expand-vertical",
        "unit_of_measurement": "mm",
        "enabled_by_default": True,
    },
    
    # Performance - enabled by default
    "max_speed": {
        "name": "Maximální rychlost",
        "icon": "mdi:speedometer",
        "unit_of_measurement": "km/h",
        "enabled_by_default": True,
    },
    "engine_power": {
        "name": "Výkon motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "kW",
        "device_class": "power",
        "enabled_by_default": True,
    },
    "engine_displacement": {
        "name": "Objem motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "cm³",
        "enabled_by_default": True,
    },
    "fuel_type": {
        "name": "Palivo",
        "icon": "mdi:gas-station",
        "enabled_by_default": True,
    },
    
    # Documents - disabled by default
    "tp_number": {
        "name": "Číslo TP",
        "icon": "mdi:card-account-details",
        "enabled_by_default": False,
    },
    "orv_number": {
        "name": "Číslo ORV",
        "icon": "mdi:card-account-details",
        "enabled_by_default": False,
    },
    
    # Registration information - disabled by default
    "first_registration": {
        "name": "Datum první registrace",
        "icon": "mdi:calendar",
        "device_class": "date",
        "enabled_by_default": False,
    },
    "first_registration_cz": {
        "name": "Datum první registrace v ČR",
        "icon": "mdi:calendar-check",
        "device_class": "date",
        "enabled_by_default": False,
    },
    
    # Additional vehicle info - disabled by default
    "category": {
        "name": "Kategorie",
        "icon": "mdi:car-info",
        "enabled_by_default": False,
    },
    "vehicle_type": {
        "name": "Typ vozidla",
        "icon": "mdi:motorbike",
        "enabled_by_default": False,
    },
    "max_weight": {
        "name": "Nejvyšší povolená hmotnost",
        "icon": "mdi:weight",
        "unit_of_measurement": "kg",
        "enabled_by_default": False,
    },
    "wheelbase": {
        "name": "Rozvor",
        "icon": "mdi:arrow-expand-horizontal",
        "unit_of_measurement": "mm",
        "enabled_by_default": False,
    },
    
    # Consumption and emissions - disabled by default
    "consumption_city": {
        "name": "Spotřeba - město",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "enabled_by_default": False,
    },
    "consumption_highway": {
        "name": "Spotřeba - mimo město",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "enabled_by_default": False,
    },
    "consumption_combined": {
        "name": "Spotřeba - kombinovaná",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "enabled_by_default": False,
    },
    "co2_emissions": {
        "name": "Emise CO2",
        "icon": "mdi:molecule-co2",
        "unit_of_measurement": "g/km",
        "enabled_by_default": False,
    },
    
    # Noise and status - disabled by default
    "noise_stationary": {
        "name": "Hluk - stojící",
        "icon": "mdi:volume-high",
        "unit_of_measurement": "dB",
        "enabled_by_default": False,
    },
    "noise_driving": {
        "name": "Hluk - jízda",
        "icon": "mdi:volume-high",
        "unit_of_measurement": "dB",
        "enabled_by_default": False,
    },
    "status_name": {
        "name": "Stav vozidla",
        "icon": "mdi:car-info",
        "enabled_by_default": False,
    },
    "owners_count": {
        "name": "Počet vlastníků",
        "icon": "mdi:account-multiple",
        "enabled_by_default": False,
    },
    "operators_count": {
        "name": "Počet provozovatelů",
        "icon": "mdi:account-multiple",
        "enabled_by_default": False,
    },
}

class STKStatus:
    VALID = "valid"
    EXPIRED = "expired"
    WARNING = "warning"  # Less than 30 days remaining
    UNKNOWN = "unknown"
