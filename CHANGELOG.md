# Changelog

## 2026-04-29 — Earth Resonance integration v1.0
- Added Schumann/Geomag fetch (NOAA Kp + Tomsk SR JPEG + solar wind)
- Added advisor: regime × planetary hour → GO/CAUTION/DEFER/RED verdict
- Patched divine-timing.py to render EARTH RESONANCE block
- Cron: every 30 min refresh
- Pitfalls documented: Tomsk SSL cert expired (use ssl bypass), NOAA `kp` field junk (use kp_index), solar wind endpoint returns LIST
- Termux TTS/notify now log structured degradation events instead of silent fail
