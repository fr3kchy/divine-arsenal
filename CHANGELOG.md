# Changelog

## 2026-04-29 — Earth Resonance integration v1.0
- Added Schumann/Geomag fetch (NOAA Kp + Tomsk SR JPEG + solar wind)
- Added advisor: regime × planetary hour → GO/CAUTION/DEFER/RED verdict
- Patched divine-timing.py to render EARTH RESONANCE block
- Cron: every 30 min refresh
- Pitfalls documented: Tomsk SSL cert expired (use ssl bypass), NOAA `kp` field junk (use kp_index), solar wind endpoint returns LIST
- Termux TTS/notify now log structured degradation events instead of silent fail

## 2026-04-29 — Earth Resonance v1.1 (post-narathon hardening)
- Added schumann_selftest.py: 8-test harness (NOAA Kp + Solar Wind fetch, Tomsk SSL bypass, regime classification, verdict matrix, missing-data graceful, stale-data detection, briefing render)
- Fixed datetime.utcnow() deprecation (3 sites) → _utcnow_iso() helper
- Added stale-data guard: advisor degrades verdict to UNKNOWN if data >90 min old
- Added is_stale() with bad-timestamp resilience
- Wired into system-health monitor: new EARTH RESONANCE block with UP/STALE/DEGRADED/DOWN status
- Selftest 8/8 passing; -W error::DeprecationWarning passes clean
