ENVIRONMENT = "simulated"   # change to "live" when dongle arrives

# OBD connection (used only in live mode)
OBD_PORT        = "/dev/tty.Vgate-BLE-Port"  # update after dongle arrives
OBD_BAUDRATE    = 38400
SAMPLE_RATE_HZ  = 2

# Simulated data path (used this week)
SIMULATED_CSV   = "data/simulated/simulated_drive.csv"

# Thresholds for Hyundai Creta
COOLANT_TEMP_MAX        = 105
RPM_IDLE_MAX            = 1000
RPM_HIGH_WARN           = 5500
FUEL_TRIM_WARN          = 10.0
BATTERY_VOLT_MIN        = 13.5
THROTTLE_SNAP_DELTA     = 30
ENGINE_LOAD_HIGH        = 85

# Models
WHISPER_MODEL           = "base.en"
LLM_URL                 = "http://localhost:11434/v1"
LLM_MODEL               = "mistral"
EMBEDDING_MODEL         = "all-MiniLM-L6-v2"

# Paths
SESSIONS_DIR            = "data/sessions"
KNOWLEDGE_BASE_PATH     = "knowledge_base/faiss_index"
EVENTS_LOG_PATH         = "knowledge_base/events.json"