#!/usr/bin/env python3
"""
schumann_fetch.py — fetch Schumann Resonance + geomagnetic state.

Primary:   Tomsk State Univ (TSU) live SR spectrogram (JPEG, requires SSL bypass)
Anchor:    NOAA SWPC Kp planetary index (1-min, JSON)
Fallback:  Kp-only mode if Tomsk unreachable

Writes:
  ~/.hermes/data/sr/latest_spectrogram.jpg   (raw image)
  ~/.hermes/data/sr/latest.json              (parsed state)
  ~/.hermes/data/sr/history.csv              (append-only timeseries)
"""
from __future__ import annotations
import json, ssl, csv, sys, os, datetime as dt, urllib.request
from pathlib import Path

DATA = Path.home() / ".hermes/data/sr"
DATA.mkdir(parents=True, exist_ok=True)

UA = "fr3k-hermes/1.0 (+schumann-monitor)"
TOMSK_IMG = "https://sosrff.tsu.ru/new/shm.jpg"
NOAA_KP   = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
NOAA_SOLAR_WIND = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"

def _get(url: str, timeout: int = 15, insecure: bool = False) -> bytes:
    ctx = ssl._create_unverified_context() if insecure else None
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()

def fetch_tomsk_spectrogram() -> dict:
    """Pull Tomsk PNG; we don't OCR pixels yet — store image + metadata."""
    out = {"source": "tomsk", "ok": False}
    try:
        img = _get(TOMSK_IMG, insecure=True)
        path = DATA / "latest_spectrogram.jpg"
        path.write_bytes(img)
        out.update({
            "ok": True,
            "bytes": len(img),
            "path": str(path),
            "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        })
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out

def fetch_noaa_kp() -> dict:
    out = {"source": "noaa_kp", "ok": False}
    try:
        raw = _get(NOAA_KP)
        rows = json.loads(raw)
        # Most-recent observation. Fields: time_tag, kp_index, kp, ...
        rows = [r for r in rows if r.get("kp_index") is not None]
        if not rows:
            raise RuntimeError("no kp rows")
        last = rows[-1]
        kp = float(last["kp_index"])
        cutoff = dt.datetime.utcnow() - dt.timedelta(hours=24)
        kp24 = []
        for r in rows[-1500:]:
            try:
                t = dt.datetime.fromisoformat(r["time_tag"].replace("Z",""))
                if t >= cutoff:
                    kp24.append(float(r["kp_index"]))
            except Exception:
                pass
        out.update({
            "ok": True,
            "kp_now": kp,
            "kp_24h_max": max(kp24) if kp24 else kp,
            "kp_24h_mean": (sum(kp24)/len(kp24)) if kp24 else kp,
            "time_tag": last.get("time_tag"),
            "samples_24h": len(kp24),
        })
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out

def fetch_noaa_solar_wind() -> dict:
    out = {"source": "noaa_sw", "ok": False}
    try:
        raw = _get(NOAA_SOLAR_WIND)
        d = json.loads(raw)
        # Endpoint returns a list with one record: [{"proton_speed": 323, "time_tag": "..."}]
        if isinstance(d, list) and d:
            d = d[0]
        speed = d.get("proton_speed") or d.get("WindSpeed") or 0
        out.update({
            "ok": True,
            "wind_speed_kms": float(speed),
            "time": d.get("time_tag") or d.get("TimeStamp"),
        })
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out

def classify_regime(kp_now: float, kp_24h_max: float, sr_ok: bool) -> tuple[str, str]:
    """Return (regime, hermetic_tone)."""
    if kp_now >= 7:
        return "STORM", "Mars"          # severe geomagnetic — disruption
    if kp_now >= 5 or kp_24h_max >= 6:
        return "ELEVATED", "Mars/Sun"   # G1+ storm window
    if kp_now >= 4:
        return "UNSETTLED", "Mercury"   # active, minor disruption
    if kp_now >= 2.5:
        return "BASELINE", "Sun"        # normal
    return "QUIET", "Saturn/Venus"      # very calm, receptive

def build_state() -> dict:
    sr = fetch_tomsk_spectrogram()
    kp = fetch_noaa_kp()
    sw = fetch_noaa_solar_wind()

    kp_now = kp.get("kp_now", 0) if kp.get("ok") else 0
    kp_max = kp.get("kp_24h_max", 0) if kp.get("ok") else 0
    regime, tone = classify_regime(kp_now, kp_max, sr.get("ok", False))

    state = {
        "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        "regime": regime,
        "hermetic_tone": tone,
        "kp_now": kp_now,
        "kp_24h_max": kp_max,
        "kp_24h_mean": kp.get("kp_24h_mean") if kp.get("ok") else None,
        "sr_fundamental_hz": 7.83,  # nominal — pixel decode roadmap'd
        "sr_image_ok": sr.get("ok", False),
        "sr_image_path": sr.get("path"),
        "solar_wind_kms": sw.get("wind_speed_kms") if sw.get("ok") else None,
        "sources": {
            "tomsk": "ok" if sr.get("ok") else sr.get("error", "fail"),
            "noaa_kp": "ok" if kp.get("ok") else kp.get("error", "fail"),
            "noaa_sw": "ok" if sw.get("ok") else sw.get("error", "fail"),
        },
    }

    # Persist
    (DATA / "latest.json").write_text(json.dumps(state, indent=2))

    hist = DATA / "history.csv"
    new = not hist.exists()
    with hist.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts","regime","kp_now","kp_24h_max","sr_ok","wind_kms"])
        w.writerow([state["fetched_at"], regime, kp_now, kp_max,
                    int(state["sr_image_ok"]), state["solar_wind_kms"] or ""])
    return state

def main():
    s = build_state()
    print(json.dumps(s, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
