#!/usr/bin/env python3
"""
schumann_selftest.py — smoke test the earth-resonance pipeline.

Tests:
  1. fetch_noaa_kp returns ok with non-stale data
  2. fetch_noaa_solar_wind parses LIST format correctly
  3. fetch_tomsk_spectrogram bypasses SSL and writes JPEG
  4. classify_regime maps Kp values correctly
  5. advisor verdict_for matrix produces expected verdicts
  6. advisor handles missing latest.json without crashing
  7. advisor stale-data detection
  8. divine-timing block renders without exception
"""
from __future__ import annotations
import sys, os, json, tempfile, datetime as dt
from pathlib import Path

SCRIPTS = Path.home() / ".hermes/scripts"
sys.path.insert(0, str(SCRIPTS))

PASS = "✓"
FAIL = "✗"

results = []

def test(name, fn):
    try:
        ok, msg = fn()
        results.append((name, ok, msg))
        icon = PASS if ok else FAIL
        print(f"  {icon} {name}: {msg}")
        return ok
    except Exception as e:
        results.append((name, False, f"EXCEPTION: {type(e).__name__}: {e}"))
        print(f"  {FAIL} {name}: EXCEPTION {type(e).__name__}: {e}")
        return False

# Hot-load modules
import importlib.util
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

sf = _load("schumann_fetch", SCRIPTS / "schumann_fetch.py")
sa = _load("schumann_advisor", SCRIPTS / "schumann_advisor.py")

# 1
def t_kp():
    r = sf.fetch_noaa_kp()
    if not r.get("ok"):
        return False, f"not ok: {r.get('error')}"
    if "kp_now" not in r:
        return False, "missing kp_now"
    return True, f"kp_now={r['kp_now']} 24h_max={r['kp_24h_max']}"

# 2
def t_sw():
    r = sf.fetch_noaa_solar_wind()
    if not r.get("ok"):
        return False, f"not ok: {r.get('error')}"
    if r.get("wind_speed_kms", 0) <= 0:
        return False, f"bad speed: {r}"
    return True, f"wind={r['wind_speed_kms']} km/s"

# 3
def t_tomsk():
    r = sf.fetch_tomsk_spectrogram()
    if not r.get("ok"):
        return False, f"not ok: {r.get('error')}"
    if r.get("bytes", 0) < 50000:
        return False, f"image too small: {r['bytes']}"
    return True, f"{r['bytes']} bytes"

# 4
def t_classify():
    cases = [
        (8, 8, "STORM"),
        (5, 5, "ELEVATED"),
        (0, 6, "ELEVATED"),
        (4, 4, "UNSETTLED"),
        (3, 3, "BASELINE"),
        (1, 1, "QUIET"),
        (0, 0, "QUIET"),
    ]
    for kp_now, kp_max, expected in cases:
        regime, _ = sf.classify_regime(kp_now, kp_max, True)
        if regime != expected:
            return False, f"kp({kp_now},{kp_max})→{regime} expected {expected}"
    return True, f"{len(cases)}/{len(cases)} matrix entries correct"

# 5
def t_verdict():
    cases = [
        ("STORM", "Mars", "RED"),
        ("STORM", "Jupiter", "DEFER"),
        ("ELEVATED", "Mars", "CAUTION"),
        ("ELEVATED", "Jupiter", "GO"),
        ("BASELINE", "Sun", "GO"),
        ("BASELINE", "Saturn", "GO"),
        ("BASELINE", "Mars", "CAUTION"),
        ("QUIET", "Venus", "GO"),
    ]
    for regime, hour, expected in cases:
        v, _ = sa.verdict_for(regime, hour)
        if v != expected:
            return False, f"({regime},{hour})→{v} expected {expected}"
    return True, f"{len(cases)}/{len(cases)} verdict matrix correct"

# 6
def t_missing_data():
    # Save real, blank it, run, restore
    real = Path.home() / ".hermes/data/sr/latest.json"
    bak = None
    if real.exists():
        bak = real.read_text()
        real.unlink()
    try:
        # Should NOT crash; main returns 2
        rc = sa.main()
        if rc != 2:
            return False, f"expected rc=2 got {rc}"
        return True, "graceful exit code 2"
    finally:
        if bak is not None:
            real.write_text(bak)

# 7
def t_stale():
    fresh = {"fetched_at": sf._utcnow_iso(), "regime": "QUIET"}
    stale_ts = (dt.datetime.now(dt.UTC) - dt.timedelta(hours=5)).isoformat().replace("+00:00", "Z")
    stale = {"fetched_at": stale_ts, "regime": "QUIET"}
    bad = {"fetched_at": "garbage"}
    s1, a1 = sa.is_stale(fresh)
    s2, a2 = sa.is_stale(stale)
    s3, _ = sa.is_stale(bad)
    if s1: return False, f"fresh marked stale (age={a1:.1f})"
    if not s2: return False, f"stale not detected (age={a2:.1f})"
    if not s3: return False, "garbage not marked stale"
    return True, f"fresh={a1:.1f}m stale={a2:.1f}m garbage=stale"

# 8
def t_briefing():
    import subprocess
    r = subprocess.run(["python3", str(SCRIPTS / "divine-timing.py")],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return False, f"divine-timing rc={r.returncode}"
    if "EARTH RESONANCE" not in r.stdout:
        return False, "EARTH RESONANCE block missing from briefing"
    return True, "EARTH RESONANCE block renders"

print("=== schumann pipeline selftest ===")
test("noaa_kp_fetch", t_kp)
test("noaa_solar_wind_fetch", t_sw)
test("tomsk_spectrogram_fetch", t_tomsk)
test("classify_regime_matrix", t_classify)
test("verdict_for_matrix", t_verdict)
test("advisor_missing_data_graceful", t_missing_data)
test("advisor_stale_data_detection", t_stale)
test("divine_timing_briefing_block", t_briefing)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print()
print(f"=== {passed}/{total} tests passed ===")
sys.exit(0 if passed == total else 1)
