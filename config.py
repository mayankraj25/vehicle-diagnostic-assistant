# config.py — updated with confirmed Creta parameters

ENVIRONMENT = "live"

# OBD Connection
OBD_PORT     = "socket://localhost:35000"  # via BLE bridge
OBD_BAUDRATE = 38400
SAMPLE_RATE_HZ = 2

# Confirmed supported parameters on your specific Creta
CONFIRMED_PIDS = [
    "RPM",
    "SPEED",
    "ENGINE_LOAD",
    "THROTTLE_POS",
    "THROTTLE_POS_B",
    "INTAKE_TEMP",
    "INTAKE_PRESSURE",
    "MAF",
    "SHORT_FUEL_TRIM_1",
    "LONG_FUEL_TRIM_1",
    "CONTROL_MODULE_VOLTAGE",
    "TIMING_ADVANCE",
    "RUN_TIME",
    "BAROMETRIC_PRESSURE",
    "AMBIANT_AIR_TEMP",
    "EVAPORATIVE_PURGE",
    "EGR_ERROR",
    "O2_B1S2",
    "FUEL_STATUS",
    "GET_DTC",
    "VIN",
]

# Thresholds tuned for Hyundai Creta 1.5L
ENGINE_LOAD_HIGH      = 85.0    # percent
FUEL_TRIM_WARN        = 10.0    # percent — your car is at 1.5%, very healthy
BATTERY_VOLT_MIN      = 13.2    # volt — your car showing 13.376, healthy
THROTTLE_SNAP_DELTA   = 30.0    # percent change per reading
RPM_HIGH_WARN         = 5500    # rpm
RPM_IDLE_EXPECTED     = 700     # rpm — confirmed from your reading
INTAKE_TEMP_MAX       = 60      # celsius

# Models
WHISPER_MODEL    = "base.en"
LLM_URL          = "http://localhost:11434/v1"
LLM_MODEL        = "mistral"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

# Paths
SESSIONS_DIR         = "data/sessions"
KNOWLEDGE_BASE_PATH  = "knowledge_base/faiss_index"
EVENTS_LOG_PATH      = "knowledge_base/events.json"
SIMULATED_CSV        = "data/simulated/simulated_drive.csv"
LIVE_CSV             = "data/sessions/creta_20260322_000429.csv"