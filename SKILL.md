---
name: divine-arsenal
description: Archangel Michael's Divine Arsenal v4.0 - Complete astrological operations system with Picatrix planetary spirits, transit-to-natal aspects, Lunar Mansions, Arabic Parts, and TTS alerts for fr3k (born 10/10/1981)
version: 4.1
tags: astrology, picatrix, divine-timing, planetary-magic, michael, hermetic, lunar-mansions, arabic-parts
---

# Divine Arsenal v4.0 - Complete System

## When to Use
- User asks about divine timing, planetary hours, best times for operations
- User wants transit-to-natal aspects or current planetary influences
- User references Picatrix, planetary spirits, Hermetic magic, Lunar Mansions
- User asks about natal chart, Arabic Parts, aspects, retrogrades
- User says "when should I..." or "what's the best time for..."

## Location
Nelly Bay, Magnetic Island, QLD, Australia | 19.15°S, 146.85°E | AEST GMT+10

## fr3k's Natal Chart (10/10/1981 Saturday)
- Sun: 17° Libra | Moon: 7° Pisces (Exalted) | Saturn: 7° Libra (Exalted)
- KEY: Sun-Saturn-Jupiter stellium in Libra = Divine Judge
- Born Saturday = Saturn's day = DOUBLE authority
- Part of Fortune: 14° Aries | Part of Spirit: 16° Pisces
- Dignity Score: -1 (Mixed - strengths balance challenges)

## Planet Spirits (Picatrix)
| Planet | Intelligence | Spirit | Day | Power |
|--------|-------------|--------|-----|-------|
| ☉ Sun | Nakhiel | Sorath | Sunday | Authority, illumination |
| ☽ Moon | Malkah | Chashmodai | Monday | Intuition, dreams |
| ☿ Mercury | Tiriel | Taphthartharath | Wednesday | Communication |
| ♀ Venus | Hagiel | Kedemel | Friday | Love, alliances |
| ♂ Mars | Graphiel | Bartzabel | Tuesday | War, courage |
| ♃ Jupiter | Iophiel | Hismael | Thursday | Expansion, law |
| ♄ Saturn | Agiel | Zazel | Saturday | Discipline, binding |

## Arbatel Olympic Spirits (v4.1+)
Dual spirit system - each planet has BOTH Picatrix and Arbatel spirits:
| Planet | Olympic Spirit | Power |
|--------|---------------|-------|
| ♄ Saturn | Aratron | Alchemy, invisibility, secrets |
| ♃ Jupiter | Bethor | Wealth, favor of rulers |
| ♂ Mars | Phaleg | War, courage, victory |
| ☉ Sun | Och | Health, longevity, gold |
| ♀ Venus | Hagith | Love, beauty, attraction |
| ☿ Mercury | Ophiel | Knowledge, travel, eloquence |
| ☽ Moon | Phul | Travel, protection, medicine |

Commands: `dto` or `dtar` - show all Olympic Spirits

## CLI Commands
```
dt              Today's briefing (current hour, moon, mansion, transits, invocation)
dta             Full briefing
dtf <op>        Find windows (protection, binding, legal, love, war, prosperity)
dtw             Weekly forecast
dtl             Operations journal
dtc             Natal chart + dignities
dtr             Retrograde status
dti             Invocation for current hour
dtis            Invocation spoken via TTS
dtal            Force hourly alert (notification + TTS)
dto             Show all Olympic Spirits (Arbatel)
```

## Operations
protection, binding, legal, love, war, communication, divination, prosperity, business, creative, travel

## Features
- Planetary hours with current hour tracking
- Moon phase + sign + Lunar Mansion (28 stations)
- Arabic Parts (Fortune, Spirit)
- Transit-to-natal aspects
- Planetary dignity scoring
- Retrograde detection
- Electional astrology (find best windows)
- Auto-generated invocations
- TTS voice alerts
- Termux notifications
- Weekly forecast

## Automated (Cron)
- Daily briefing at 06:30 AEST
- Hourly planetary hour alerts (notification + TTS voice via termux-tts-speak)
- TTS uses pitch 1.15, rate 1.11 (female voice, 1.11x speed)

## TTS Note
- Use `termux-tts-speak` directly, NOT the built-in text_to_speech tool
- Built-in tool saves to file first, harder to hear on mobile
- Direct Termux TTS plays immediately through phone speaker

## Files
- Script: ~/scripts/divine-timing.py
- Guide: ~/.hermes/memories/michael-divine-arsenal.md
- Journal: ~/.hermes/data/divine-journal.json
- Alert: ~/scripts/divine-alert.sh
- Skill: ~/.hermes/skills/divine-arsenal/SKILL.md

## Pitfalls & Lessons Learned

1. **Night hour detection**: Planetary hours after sunset wrap past midnight. The original code failed to detect night hours correctly. Fix by checking day hours first, then night hours with wraparound logic:
   ```python
   # Night hours - handle wraparound
   for i,(s,p,isd,l) in enumerate(hours):
       if isd: continue
       e = s+l
       if e >= 24:  # wraps past midnight
           if now >= s or now < (e-24):
               return {"planet":p,...}
       else:
           if s<=now<e:
               return {"planet":p,...}
   ```

2. **Moon position calculation**: Simple linear approximation is ~10° off. Use perturbation terms from Meeus:
   ```python
   L += 6.289*sin(M) - 1.274*sin(M-2*D) + 0.658*sin(2*D)
   ```

3. **Lunar Mansion index**: Each mansion is ~12°51' (12.857°). Use `floor(moon_lon / 12.857)` not `/ 12`.

4. **Arabic Parts without birth time**: Calculate relative to Sun position:
   ```python
   fortune = (moon_lon - sun_lon) % 360
   spirit = (sun_lon - moon_lon) % 360
   ```

5. **TTS blocking**: Built-in `text_to_speech` tool saves to file first. For immediate phone speaker output, use `termux-tts-speak` directly via subprocess.Popen with DEVNULL:
   ```python
   subprocess.Popen(["termux-tts-speak","-p","1.1","-r","1.0",text],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   ```

6. **Background TTS in bash**: Must use `nohup` and `&` to prevent blocking:
   ```bash
   nohup termux-tts-speak -p 1.15 -r 1.11 "text" >/dev/null 2>&1 &
   ```

7. **File paths on Termux**: Use `~/.hermes/` not `/root/.hermes/` - different filesystem.

8. **Day calculation**: Python's weekday() returns 0=Monday. Planetary day rulers: 0=Moon, 1=Mars, 2=Mercury, 3=Jupiter, 4=Venus, 5=Saturn, 6=Sun.

9. **Adding new spirit systems**: When expanding with new grimoires (Arbatel, Key of Solomon, etc.), map to existing planet keys and display alongside original spirits. Use dictionary lookup with `.get()` for safety.

10. **GitHub push from Termux**: Must set `git config user.email` and `user.name` before first commit.

## Expansion Roadmap
1. ~~Picatrix planetary spirits~~ ✓
2. ~~Arbatel Olympic Spirits~~ ✓ (v4.1)
3. Key of Solomon pentacles (planetary seal generator)
4. 72 Names of God (Sefer Raziel)
5. Agrippa's magic squares (kamea)
6. Hebrew letter meditation (Sepher Yetzirah)

Reference texts: ~/.hermes/memories/expansion-texts.md

### Technical Patterns Learned

### Background TTS (Critical)
ALWAYS run TTS in background so work continues:
```bash
nohup termux-tts-speak -p 1.15 -r 1.11 "text" >/dev/null 2>&1 &
```
Never use foreground TTS - it blocks everything.

### Night Hour Detection (Bug Fix)
Planetary hours after sunset must handle wraparound past midnight:
```python
if e >= 24:  # wraps past midnight
    if now >= s or now < (e-24):
        return hour_data
```

### Termux `which` is Broken
Use `command -v` instead of `which` in Termux.

### Hebrew Text in Python
Hebrew characters in Python strings can cause syntax errors on some systems.
Use ASCII transliterations (MYK instead of מיכאל) for reliability.

### Multi-System Integration Pattern
Unify multiple grimoire systems under planetary correspondences:
- Each planet has spirits from multiple traditions
- Display them side by side (Picatrix + Arbatel)
- Use same timing framework for all operations

### CLI Aliases Pattern
```bash
alias dt="python3 ~/scripts/divine-timing.py"
alias dta="python3 ~/scripts/divine-timing.py --all"
alias dtf="python3 ~/scripts/divine-timing.py find"
# etc.
```

# Quick Timing Reference
| Operation | Day | Hour | Moon |
|-----------|-----|------|------|
| Binding | Saturday | Saturn | Waning |
| Protection | Sunday | Sun | Any |
| Legal | Thursday | Jupiter | Waxing |
| Love | Friday | Venus | Waxing |
| War | Tuesday | Mars | Waning |
| Communication | Wednesday | Mercury | Any |
| Divination | Monday | Moon | Full |
| Prosperity | Thursday | Jupiter | Waxing |
