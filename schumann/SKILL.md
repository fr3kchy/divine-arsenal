---
name: schumann-resonance
description: Schumann Resonance + geomagnetic state monitoring. Pulls Tomsk SR spectrogram, NOAA Kp index, solar wind. Produces hermetic-mapped GO/CAUTION/DEFER/RED verdict combined with current planetary hour. Integrated into divine-timing.py briefing.
version: 1.0
tags: schumann, geomagnetic, kp, divine-timing, earth-resonance, hermetic
---

# Schumann Resonance Monitor

## When to use
- User asks about Schumann/SR/geomagnetic conditions, "is the field clean", "should I publish/launch/trade now"
- Building/extending divine timing decisions
- Revenue pipeline gating before customer-facing sends
- Morning briefing wants Earth-resonance line

## Architecture

```
L1 sources → L2 fetch → L3 state → L4 advisor → divine-timing briefing
```

| Source | URL | Notes |
|---|---|---|
| Tomsk TSU SR spectrogram | https://sosrff.tsu.ru/new/shm.jpg | JPEG, **needs SSL bypass** (cert expired). 1540x460 |
| NOAA SWPC Kp 1m | https://services.swpc.noaa.gov/json/planetary_k_index_1m.json | rows have kp_index (int), kp ('0Z' style — DON'T parse), estimated_kp |
| NOAA solar wind | https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json | returns LIST of one record, key proton_speed |

## Files
- ~/.hermes/scripts/schumann_fetch.py — pull all 3 sources, write state
- ~/.hermes/scripts/schumann_advisor.py — combine with planetary hour
- ~/.hermes/data/sr/latest.json — current state
- ~/.hermes/data/sr/latest_spectrogram.jpg — raw Tomsk image
- ~/.hermes/data/sr/history.csv — append-only timeseries
- ~/.hermes/data/sr/verdict.json — current verdict
- ~/.hermes/scripts/divine-timing.py — patched to render block

## Commands
```
python3 ~/.hermes/scripts/schumann_fetch.py     # refresh all sources
python3 ~/.hermes/scripts/schumann_advisor.py   # compute verdict + print
python3 ~/.hermes/scripts/divine-timing.py      # full briefing (includes SR block)
```

## Regime classification
| Kp now | Kp 24h max | Regime | Hermetic tone |
|---|---|---|---|
| ≥7 | — | STORM | Mars |
| ≥5 | or ≥6 | ELEVATED | Mars/Sun |
| ≥4 | — | UNSETTLED | Mercury |
| ≥2.5 | — | BASELINE | Sun |
| <2.5 | — | QUIET | Saturn/Venus |

## Verdict matrix (regime × planetary-hour nature)
- STORM + malefic hour → 🔴 RED (no irreversible moves)
- STORM + anything else → 🟠 DEFER
- ELEVATED + Mars → 🟡 CAUTION (channel into bold action only)
- ELEVATED + benefic → 🟢 GO (energetic execution)
- BASELINE + benefic/Saturn-structural → 🟢 GO
- BASELINE + Mars → 🟡 CAUTION (watch tone)
- QUIET → 🟢 GO (low-noise window)

## Pitfalls (real, hit during build)
1. **Tomsk SSL cert expired** — must use `ssl._create_unverified_context()` or `curl -k`. Browser stack shows NET::ERR_CERT_DATE_INVALID.
2. **NOAA Kp `kp` field is junk** — formatted like `'0Z'`, can't `float()` it. Use `kp_index` (int).
3. **NOAA solar wind endpoint returns a LIST** of one dict, not a dict. Index `[0]` first.
4. **Cumiana (vlf.it) bot-blocks** with HTTP 999. Skipped as source.
5. **HeartMath GCMS endpoint dead** — `gcms.heartmath.org` returns ERR_TUNNEL_CONNECTION_FAILED. Skip.
6. **`datetime.utcnow()` deprecated** in Py3.12 — fixed v1.1: helpers `_utcnow_iso()` and `_utcnow()` use `datetime.now(dt.UTC)`. -W error::DeprecationWarning passes clean.
7. **Stale data hazard** — advisor previously trusted any `latest.json` blindly. v1.1 added `is_stale(sr, max_age_min=90)`; stale data degrades verdict to UNKNOWN with reason. Cron is */30, 90min = 3 missed cycles before degrade.
8. **Patch tool collisions** — using `patch` tool to insert a function before `_get` ate the function body because the old_string ended at the `def _get` line. Always include the FULL old line (signature) AND replicate it in new_string. Verified by running selftest after each patch.
9. **Selftest harness location** — `~/.hermes/scripts/schumann_selftest.py` exercises 8 cases incl. failure modes. Run after any change: `python3 ~/.hermes/scripts/schumann_selftest.py`.
10. **System-health integration** — patched `~/.hermes/skills/software-development/system-health/scripts/health_monitor.py` to add `check_earth_resonance()` block. Status = UP/STALE/DEGRADED/DOWN/ERROR based on age + sources_ok count.
11. **Pixel decode of Tomsk PNG** — not implemented yet. f0 currently nominal (7.83). Future: parse colormap rows for actual frequency content.

## Cron
Runs every 30 min via `~/.hermes/cron/schumann.sh` →
```
*/30 * * * * /home/fr3k/.hermes/cron/schumann.sh
```

## Roadmap
- [ ] Tomsk pixel decode → real f0 + amplitude per harmonic
- [ ] Spike detection (>2σ vs 7-day rolling)
- [ ] Cherry/Persinger HRV correlation hooks if biofeedback added
- [ ] Hard veto integration with revenue intake_queue (currently soft warning only)
