import obd
import csv
import time
import os
from datetime import datetime
from config import OBD_PORT, OBD_BAUDRATE, SAMPLE_RATE_HZ

# Custom coolant PID since Creta needs raw query
COOLANT_PID = obd.OBDCommand(
    "COOLANT_TEMP",
    "Engine Coolant Temp",
    b"0105",
    7,
    obd.decoders.temp,
    obd.ECU.ENGINE,
    True
)

PARAMETERS = [
    obd.commands.RPM,
    obd.commands.SPEED,
    obd.commands.ENGINE_LOAD,
    obd.commands.THROTTLE_POS,
    obd.commands.INTAKE_TEMP,
    obd.commands.INTAKE_PRESSURE,
    obd.commands.MAF,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.LONG_FUEL_TRIM_1,
    obd.commands.CONTROL_MODULE_VOLTAGE,
    obd.commands.TIMING_ADVANCE,
    obd.commands.BAROMETRIC_PRESSURE,
    obd.commands.AMBIANT_AIR_TEMP,
    obd.commands.GET_DTC,
    COOLANT_PID,
]

HEADERS = [
    "timestamp",
    "elapsed_seconds",
    "rpm",
    "speed_kmh",
    "engine_load_pct",
    "throttle_pos_pct",
    "intake_temp_c",
    "intake_pressure_kpa",
    "maf_g_per_sec",
    "short_fuel_trim_pct",
    "long_fuel_trim_pct",
    "battery_voltage",
    "timing_advance_deg",
    "barometric_pressure_kpa",
    "ambient_air_temp_c",
    "coolant_temp_c",
    "dtc_codes",
]

def safe_value(response):
    if response is None or response.is_null():
        return None
    val = response.value
    if hasattr(val, 'magnitude'):
        return round(val.magnitude, 3)
    return str(val)

def create_filename():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data/sessions", exist_ok=True)
    return f"data/sessions/creta_{ts}.csv"

def run_logger():
    filename = create_filename()
    interval = 1.0 / SAMPLE_RATE_HZ

    print(f"Connecting to Creta via bridge...")
    time.sleep(2)

    connection = obd.OBD(
        portstr=OBD_PORT,
        baudrate=OBD_BAUDRATE,
        fast=False,
        timeout=30
    )

    if not connection.is_connected():
        print("Not connected. Make sure ble_bridge.py is running.")
        return

    print(f"Connected. Logging to: {filename}")
    print("Press Ctrl+C to stop.\n")

    start_time = time.time()

    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()

        try:
            while True:
                loop_start = time.time()
                now        = datetime.now()
                elapsed    = round(time.time() - start_time, 2)

                # Query all parameters
                rpm      = safe_value(connection.query(obd.commands.RPM))
                speed    = safe_value(connection.query(obd.commands.SPEED))
                load     = safe_value(connection.query(obd.commands.ENGINE_LOAD))
                throttle = safe_value(connection.query(obd.commands.THROTTLE_POS))
                intake_t = safe_value(connection.query(obd.commands.INTAKE_TEMP))
                intake_p = safe_value(connection.query(obd.commands.INTAKE_PRESSURE))
                maf      = safe_value(connection.query(obd.commands.MAF))
                stft     = safe_value(connection.query(obd.commands.SHORT_FUEL_TRIM_1))
                ltft     = safe_value(connection.query(obd.commands.LONG_FUEL_TRIM_1))
                voltage  = safe_value(connection.query(obd.commands.CONTROL_MODULE_VOLTAGE))
                timing   = safe_value(connection.query(obd.commands.TIMING_ADVANCE))
                baro     = safe_value(connection.query(obd.commands.BAROMETRIC_PRESSURE))
                amb_temp = safe_value(connection.query(obd.commands.AMBIANT_AIR_TEMP))
                coolant  = safe_value(connection.query(COOLANT_PID, force=True))
                dtc_resp = connection.query(obd.commands.GET_DTC)
                dtcs     = str([str(d) for d in dtc_resp.value]) \
                           if not dtc_resp.is_null() else "[]"

                row = {
                    "timestamp":              now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "elapsed_seconds":        elapsed,
                    "rpm":                    rpm,
                    "speed_kmh":              speed,
                    "engine_load_pct":        load,
                    "throttle_pos_pct":       throttle,
                    "intake_temp_c":          intake_t,
                    "intake_pressure_kpa":    intake_p,
                    "maf_g_per_sec":          maf,
                    "short_fuel_trim_pct":    stft,
                    "long_fuel_trim_pct":     ltft,
                    "battery_voltage":        voltage,
                    "timing_advance_deg":     timing,
                    "barometric_pressure_kpa":baro,
                    "ambient_air_temp_c":     amb_temp,
                    "coolant_temp_c":         coolant,
                    "dtc_codes":              dtcs,
                }

                writer.writerow(row)
                f.flush()

                # Live terminal display
                print(
                    f"[{now.strftime('%H:%M:%S')}] "
                    f"RPM:{rpm:>6} | "
                    f"Speed:{speed:>5} | "
                    f"Load:{load:>5}% | "
                    f"Throttle:{throttle:>5}% | "
                    f"Battery:{voltage}V | "
                    f"Coolant:{coolant}C"
                )

                # Maintain sample rate
                sleep_time = max(0, interval - (time.time() - loop_start))
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print(f"\nSession saved to: {filename}")
            connection.close()

if __name__ == "__main__":
    run_logger()