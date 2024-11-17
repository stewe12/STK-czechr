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
    # Core STK sensors - enabled by default
    "valid_until": {
        "name": "Platnost STK",
        "icon": "mdi:calendar-clock",
        "device_class": "date",
        "api_field": "PravidelnaTechnickaProhlidkaDo",
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
    
    # Registration information - disabled by default
    "first_registration": {
        "name": "Datum první registrace",
        "icon": "mdi:calendar",
        "device_class": "date",
        "api_field": "DatumPrvniRegistrace",
        "enabled_by_default": False,
    },
    "first_registration_cz": {
        "name": "Datum první registrace v ČR",
        "icon": "mdi:calendar-check",
        "device_class": "date",
        "api_field": "DatumPrvniRegistraceVCr",
        "enabled_by_default": False,
    },
    
    # Vehicle identification - disabled by default
    "brand": {
        "name": "Značka",
        "icon": "mdi:car",
        "api_field": "TovarniZnacka",
        "enabled_by_default": False,
    },
    "model": {
        "name": "Model",
        "icon": "mdi:car-side",
        "api_field": "ObchodniOznaceni",
        "enabled_by_default": False,
    },
    "vin": {
        "name": "VIN",
        "icon": "mdi:identifier",
        "api_field": "VIN",
        "enabled_by_default": False,
    },
    "category": {
        "name": "Kategorie",
        "icon": "mdi:car-info",
        "api_field": "Kategorie",
        "enabled_by_default": False,
    },
    
    # Physical characteristics - disabled by default
    "color": {
        "name": "Barva",
        "icon": "mdi:palette",
        "api_field": "VozidloKaroserieBarva",
        "enabled_by_default": False,
    },
    "weight": {
        "name": "Provozní hmotnost",
        "icon": "mdi:weight",
        "unit_of_measurement": "kg",
        "api_field": "HmotnostiProvozni",
        "enabled_by_default": False,
    },
    "max_weight": {
        "name": "Nejvyšší povolená hmotnost",
        "icon": "mdi:weight",
        "unit_of_measurement": "kg",
        "api_field": "HmotnostiPov",
        "enabled_by_default": False,
    },
    
    # Dimensions - disabled by default
    "length": {
        "name": "Délka",
        "icon": "mdi:arrow-expand-horizontal",
        "unit_of_measurement": "mm",
        "api_field": "RozmeryDelka",
        "enabled_by_default": False,
    },
    "width": {
        "name": "Šířka",
        "icon": "mdi:arrow-expand-horizontal",
        "unit_of_measurement": "mm",
        "api_field": "RozmerySirka",
        "enabled_by_default": False,
    },
    "height": {
        "name": "Výška",
        "icon": "mdi:arrow-expand-vertical",
        "unit_of_measurement": "mm",
        "api_field": "RozmeryVyska",
        "enabled_by_default": False,
    },
    
    # Engine and performance - disabled by default
    "engine_power": {
        "name": "Výkon motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "kW",
        "device_class": "power",
        "api_field": "MotorMaxVykon",
        "enabled_by_default": False,
    },
    "engine_displacement": {
        "name": "Objem motoru",
        "icon": "mdi:engine",
        "unit_of_measurement": "cm³",
        "api_field": "MotorZdvihObjem",
        "enabled_by_default": False,
    },
    "fuel_type": {
        "name": "Palivo",
        "icon": "mdi:gas-station",
        "api_field": "Palivo",
        "enabled_by_default": False,
    },
    "max_speed": {
        "name": "Maximální rychlost",
        "icon": "mdi:speedometer",
        "unit_of_measurement": "km/h",
        "api_field": "NejvyssiRychlost",
        "enabled_by_default": False,
    },
    
    # Consumption and emissions - disabled by default
    "fuel_consumption_city": {
        "name": "Spotřeba - město",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "api_field": "SpotrebaNa100KmMesto",
        "enabled_by_default": False,
    },
    "fuel_consumption_highway": {
        "name": "Spotřeba - mimo město",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "api_field": "SpotrebaNa100Km90",
        "enabled_by_default": False,
    },
    "fuel_consumption_combined": {
        "name": "Spotřeba - kombinovaná",
        "icon": "mdi:fuel",
        "unit_of_measurement": "l/100km",
        "device_class": "gas",
        "api_field": "SpotrebaNa100Km120",
        "enabled_by_default": False,
    },
    "co2_emissions": {
        "name": "Emise CO2",
        "icon": "mdi:molecule-co2",
        "unit_of_measurement": "g/km",
        "api_field": "EmiseCO2",
        "enabled_by_default": False,
    },
}

# API endpoints
API_ENDPOINT = "https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo"

class STKStatus:
    VALID = "valid"
    EXPIRED = "expired"
    WARNING = "warning"  # Less than 30 days remaining
    UNKNOWN = "unknown"
