#!/usr/bin/env python3
"""
schumann_advisor.py — combine Schumann/Geomag state with planetary hour
to produce a GO / CAUTION / DEFER / RED verdict.

Reads:  ~/.hermes/data/sr/latest.json
Writes: ~/.hermes/data/sr/verdict.json
Prints: short text block for embedding in briefings.
"""
from __future__ import annotations
import json, sys, datetime as dt
from pathlib import Path

SR = Path.home() / ".hermes/data/sr/latest.json"
OUT = Path.home() / ".hermes/data/sr/verdict.json"

# Map planetary-hour ruler -> nature
HOUR_NATURE = {
    "Sun":     "benefic-active",
    "Jupiter": "benefic-expansive",
    "Venus":   "benefic-receptive",
    "Moon":    "neutral-receptive",
    "Mercury": "neutral-analytic",
    "Mars":    "malefic-active",
    "Saturn":  "malefic-structural",
}

# Decision matrix: (regime, hour_nature) -> (verdict, reason)
def verdict_for(regime: str, hour_ruler: str) -> tuple[str, str]:
    nat = HOUR_NATURE.get(hour_ruler, "unknown")
    r = regime.upper()

    if r == "STORM":
        if nat in ("malefic-active", "malefic-structural"):
            return "RED", f"Geomagnetic STORM compounded by {hour_ruler} hour. No irreversible moves."
        return "DEFER", f"Geomagnetic STORM under {hour_ruler}. Observe; postpone decisions."

    if r == "ELEVATED":
        if nat == "malefic-active":
            return "CAUTION", f"Elevated geomag + Mars hour: high-charge window. Channel into bold action only."
        if nat.startswith("benefic"):
            return "GO", f"Elevated activity but {hour_ruler} supports — favorable for energetic execution."
        return "CAUTION", f"Elevated geomag under {hour_ruler}. Proceed with discipline."

    if r == "UNSETTLED":
        return "CAUTION", f"Unsettled field, {hour_ruler} hour. Routine work OK; defer launches."

    if r == "BASELINE":
        if nat.startswith("benefic"):
            return "GO", f"Clean field + {hour_ruler} hour. Stack favorable — ship/launch/publish."
        if nat == "malefic-structural":
            return "GO", f"Clean field + Saturn structural hour. Peak window for audit/code/governance."
        if nat == "malefic-active":
            return "CAUTION", f"Clean field but Mars hour. Action OK; watch the tone."
        return "GO", f"Clean field, {hour_ruler} hour. Proceed."

    if r == "QUIET":
        if nat == "benefic-receptive" or nat == "neutral-receptive":
            return "GO", f"Very quiet field + {hour_ruler}. Peak for inner work, planning, partnerships."
        if nat == "malefic-structural":
            return "GO", f"Quiet field + Saturn. Deep-focus sweet spot."
        return "GO", f"Quiet field, {hour_ruler} hour. Low-noise window."

    return "UNKNOWN", f"Regime={regime} hour={hour_ruler}"

def load_sr() -> dict | None:
    if not SR.exists():
        return None
    try:
        return json.loads(SR.read_text())
    except Exception:
        return None

def is_stale(sr: dict, max_age_min: int = 90) -> tuple[bool, float]:
    """Return (is_stale, age_minutes). Treat unparseable timestamps as stale."""
    try:
        ft = sr.get("fetched_at", "")
        # Parse ISO with optional 'Z'
        ts = dt.datetime.fromisoformat(ft.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=dt.UTC)
        age = (dt.datetime.now(dt.UTC) - ts).total_seconds() / 60.0
        return (age > max_age_min, age)
    except Exception:
        return (True, -1.0)

def current_planetary_hour() -> str:
    """Shell out to divine-timing.py and parse current hour ruler."""
    import subprocess, re
    try:
        out = subprocess.run(
            ["python3", str(Path.home() / ".hermes/scripts/divine-timing.py")],
            capture_output=True, text=True, timeout=15
        ).stdout
        m = re.search(r"CURRENT HOUR:\s*\S+\s*(\w+)", out)
        if m:
            return m.group(1).capitalize()
    except Exception:
        pass
    return "Unknown"

def main():
    sr = load_sr()
    if not sr:
        print("ERROR: no SR data — run schumann_fetch.py first", file=sys.stderr)
        return 2
    hour = current_planetary_hour()
    stale, age_min = is_stale(sr)
    verdict, reason = verdict_for(sr.get("regime","UNKNOWN"), hour)
    if stale:
        # Don't trust stale verdict — degrade to UNKNOWN, advisory only
        verdict = "UNKNOWN"
        reason = f"SR data stale (age {age_min:.0f} min). Last regime: {sr.get('regime')}. Refresh fetcher before relying."
    out = {
        "computed_at": dt.datetime.now(dt.UTC).isoformat(),
        "verdict": verdict,
        "reason": reason,
        "regime": sr.get("regime"),
        "hour_ruler": hour,
        "kp_now": sr.get("kp_now"),
        "kp_24h_max": sr.get("kp_24h_max"),
        "wind_kms": sr.get("solar_wind_kms"),
        "hermetic_tone": sr.get("hermetic_tone"),
        "data_age_min": round(age_min, 1),
        "stale": stale,
    }
    OUT.write_text(json.dumps(out, indent=2))

    # Pretty print
    icon = {"GO":"🟢","CAUTION":"🟡","DEFER":"🟠","RED":"🔴","UNKNOWN":"⚪"}.get(verdict,"?")
    print("=" * 65)
    print(f"  ⚡ EARTH-RESONANCE VERDICT: {icon} {verdict}")
    print("=" * 65)
    print(f"  Regime:   {sr.get('regime')} (tone: {sr.get('hermetic_tone')})")
    print(f"  Hour:     {hour}")
    print(f"  Kp now:   {sr.get('kp_now')}   24h max: {sr.get('kp_24h_max')}")
    print(f"  Wind:     {sr.get('solar_wind_kms')} km/s")
    print(f"  SR feed:  {'ok' if sr.get('sr_image_ok') else 'DOWN'}")
    print(f"  Age:      {age_min:.1f} min{' ⚠ STALE' if stale else ''}")
    print()
    print(f"  → {reason}")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())
