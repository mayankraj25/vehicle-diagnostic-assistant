import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Simulate a 20-minute drive with realistic Creta values
DURATION_SECONDS = 1200   # 20 minutes
SAMPLE_RATE      = 2      # readings per second
TOTAL_ROWS       = DURATION_SECONDS * SAMPLE_RATE

timestamps = [datetime(2024, 3, 15, 9, 0, 0) + 
              timedelta(seconds=i/SAMPLE_RATE) 
              for i in range(TOTAL_ROWS)]

elapsed = [i / SAMPLE_RATE for i in range(TOTAL_ROWS)]
t       = np.linspace(0, DURATION_SECONDS, TOTAL_ROWS)

# ── Simulate realistic engine behaviour ──────────────────────────────────────

# RPM — idle at start, rises as driving begins, varies with acceleration
rpm_base = np.where(t < 60, 800,                      # idle first minute
           np.where(t < 120, 800 + (t-60)*25,         # accelerating
           np.where(t < 900, 2000 + 800*np.sin(t/30), # normal driving
           np.where(t < 1000, 1800 + 600*np.sin(t/20),# slowing
           800))))                                      # idle at end
rpm = rpm_base + np.random.normal(0, 30, TOTAL_ROWS)
rpm = np.clip(rpm, 700, 5500)

# Speed — 0 to ~60 kmh during drive
speed = np.where(t < 60, 0,
        np.where(t < 120, (t-60),
        np.where(t < 900, 40 + 20*np.sin(t/45),
        np.where(t < 1000, 60 - (t-900)*0.6,
        0))))
speed = speed + np.random.normal(0, 1, TOTAL_ROWS)
speed = np.clip(speed, 0, 80)

# Coolant temp — cold start, warms to 90, then FAULT at minute 15
coolant = np.where(t < 300, 30 + t*0.2,              # cold start warming
          np.where(t < 900, 90 + np.random.normal(0, 0.5, TOTAL_ROWS),  # normal
          np.where(t < 1100, 90 + (t-900)*0.07,      # slowly rising (fault)
          105 + np.random.normal(0, 0.3, TOTAL_ROWS)))) # overheating zone
coolant = np.clip(coolant, 25, 110)

# Throttle position
throttle = np.where(t < 60, 0,
           np.where(t < 120, (t-60)*0.5,
           np.where(t < 900, 15 + 20*np.abs(np.sin(t/30)),
           np.where(t < 1000, 10 + 10*np.abs(np.sin(t/20)),
           0))))
throttle = throttle + np.random.normal(0, 1, TOTAL_ROWS)
throttle = np.clip(throttle, 0, 100)

# Engine load
engine_load = 20 + 0.4*throttle + np.random.normal(0, 2, TOTAL_ROWS)
engine_load = np.clip(engine_load, 15, 100)

# Fuel trims — normal until minute 12 then drift (simulated injector issue)
short_fuel_trim = np.where(t < 720, np.random.normal(1.5, 0.5, TOTAL_ROWS),
                  np.where(t < 900, 1.5 + (t-720)*0.01,
                  np.random.normal(4.5, 0.5, TOTAL_ROWS)))

long_fuel_trim  = np.where(t < 720, np.random.normal(2.3, 0.3, TOTAL_ROWS),
                  np.where(t < 900, 2.3 + (t-720)*0.008,
                  np.where(t < 1000, 2.3 + (t-900)*0.015 + 1.5,
                  np.random.normal(11.5, 0.4, TOTAL_ROWS))))

# Battery voltage — slight dip under load
battery_voltage = np.where(rpm < 900, 12.8 + np.random.normal(0, 0.05, TOTAL_ROWS),
                  14.1 - 0.0001*rpm + np.random.normal(0, 0.05, TOTAL_ROWS))
battery_voltage = np.clip(battery_voltage, 12.5, 14.5)

# MAF
maf = 2 + 0.005*rpm + np.random.normal(0, 0.2, TOTAL_ROWS)
maf = np.clip(maf, 1.5, 30)

# Intake temp
intake_temp = 32 + 0.005*t + np.random.normal(0, 0.5, TOTAL_ROWS)

# DTCs — none until overheating zone
dtcs = np.where(t < 900, "[]",
       np.where(t < 1000, "[]",
       "['P0217']"))   # P0217 = Engine Overtemperature

df = pd.DataFrame({
    "timestamp":           [ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] for ts in timestamps],
    "elapsed_seconds":     elapsed,
    "rpm":                 np.round(rpm, 0).astype(int),
    "speed_kmh":           np.round(speed, 1),
    "coolant_temp_c":      np.round(coolant, 1),
    "intake_temp_c":       np.round(intake_temp, 1),
    "throttle_pos_pct":    np.round(throttle, 1),
    "engine_load_pct":     np.round(engine_load, 1),
    "short_fuel_trim_pct": np.round(short_fuel_trim, 2),
    "long_fuel_trim_pct":  np.round(long_fuel_trim, 2),
    "maf_g_per_sec":       np.round(maf, 2),
    "battery_voltage":     np.round(battery_voltage, 2),
    "dtc_codes":           dtcs,
})

os.makedirs("data/simulated", exist_ok=True)
df.to_csv("data/simulated/simulated_drive.csv", index=False)
print(f"Generated {TOTAL_ROWS} rows of simulated drive data.")
print(f"Faults embedded at:")
print(f"  - Minute 12: Long term fuel trim starts drifting above 10%")
print(f"  - Minute 15: Coolant temp begins rising above 105C")
print(f"  - Minute 17: DTC P0217 (Engine Overtemperature) triggered")