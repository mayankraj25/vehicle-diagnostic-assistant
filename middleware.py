import pandas as pd
import numpy as np
from config import *

def load_data(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

def compute_features(df):

    # Rate of change of coolant temperature per minute
    df["coolant_dT_dt"] = df["coolant_temp_c"].diff() / \
                          (df["elapsed_seconds"].diff() / 60)

    # Rolling average RPM over last 10 seconds (20 samples at 2Hz)
    df["rpm_rolling"] = df["rpm"].rolling(window=20).mean()

    # RPM variance — high variance at constant speed = rough engine
    df["rpm_variance"] = df["rpm"].rolling(window=20).std()

    # Throttle snap — how fast throttle is changing
    df["throttle_snap"] = df["throttle_pos_pct"].diff().abs()

    return df

def detect_events(df):
    events = []

    for idx, row in df.iterrows():
        ts = str(row["timestamp"])

        # Coolant overtemperature
        if row["coolant_temp_c"] > COOLANT_TEMP_MAX:
            events.append({
                "timestamp": ts,
                "severity":  "critical",
                "system":    "cooling",
                "event":     f"Coolant temperature reached {row['coolant_temp_c']:.1f}C. "
                             f"Critical overtemperature threshold exceeded."
            })

        # Coolant rising fast
        elif pd.notna(row.get("coolant_dT_dt")) and row["coolant_dT_dt"] > 1.5:
            events.append({
                "timestamp": ts,
                "severity":  "warning",
                "system":    "cooling",
                "event":     f"Coolant temperature rising at "
                             f"{row['coolant_dT_dt']:.1f}C per minute. "
                             f"Current temp: {row['coolant_temp_c']:.1f}C."
            })

        # Long term fuel trim warning
        if abs(row["long_fuel_trim_pct"]) > FUEL_TRIM_WARN:
            events.append({
                "timestamp": ts,
                "severity":  "warning",
                "system":    "fuel",
                "event":     f"Long term fuel trim at {row['long_fuel_trim_pct']:.1f}%. "
                             f"ECU compensating significantly for fuel mixture deviation."
            })

        # Battery voltage low
        if row["battery_voltage"] < BATTERY_VOLT_MIN:
            events.append({
                "timestamp": ts,
                "severity":  "warning",
                "system":    "electrical",
                "event":     f"Battery voltage dropped to {row['battery_voltage']:.2f}V. "
                             f"Possible alternator or battery issue."
            })

        # High RPM warning
        if row["rpm"] > RPM_HIGH_WARN:
            events.append({
                "timestamp": ts,
                "severity":  "warning",
                "system":    "engine",
                "event":     f"Engine RPM at {row['rpm']} — approaching redline."
            })

        # DTC codes
        if row["dtc_codes"] != "[]" and row["dtc_codes"] != "nan":
            events.append({
                "timestamp": ts,
                "severity":  "critical",
                "system":    "diagnostics",
                "event":     f"Diagnostic trouble code detected: {row['dtc_codes']}. "
                             f"Check engine system immediately."
            })

    # Deduplicate — keep only one event per system per 30-second window
    events = deduplicate_events(events, window_seconds=30)
    return events

def deduplicate_events(events, window_seconds=30):
    """Avoid flooding the knowledge base with identical repeated events."""
    seen = {}
    deduped = []
    for e in events:
        key = e["system"] + e["severity"]
        ts  = pd.Timestamp(e["timestamp"])
        if key not in seen or (ts - seen[key]).seconds > window_seconds:
            deduped.append(e)
            seen[key] = ts
    return deduped

def run_middleware(csv_path):
    df     = load_data(csv_path)
    df     = compute_features(df)
    events = detect_events(df)
    return events