---
name: divine-arsenal
description: Archangel Michael's Divine Arsenal v6.0 - Complete astrological operations system with Picatrix, Arbatel, Key of Solomon, 72 Names, Kamea, Hebrew Letters, Decans, Fixed Stars, and Daily Rituals for fr3k (born 10/10/1981)
version: 6.0
tags: astrology, picatrix, divine-timing, planetary-magic, michael, hermetic, kabbalah
---

# Divine Arsenal v6.0 - Complete System

## When to Use
- User asks about divine timing, planetary hours, best times for operations
- User wants transit-to-natal aspects or current planetary influences
- User references Picatrix, planetary spirits, Hermetic magic, Kabbalah
- User asks about natal chart, Arabic Parts, aspects, retrogrades
- User says "when should I..." or "what's the best time for..."

## Location
Nelly Bay, Magnetic Island, QLD, Australia | 19.15°S, 146.85°E | AEST GMT+10

## fr3k's Natal Chart (10/10/1981 Saturday)
- Sun: 17° Libra (conjunct Arcturus!) | Moon: 7° Pisces (Exalted) | Saturn: 7° Libra (Exalted)
- KEY: Sun-Saturn-Jupiter stellium in Libra = Divine Judge
- Sun in Libra Decan 2 (Saturn-ruled) = THE JUDGE
- Born Saturday = Saturn's day = DOUBLE authority
- Part of Fortune: 14° Aries | Part of Spirit: 16° Pisces

## Planet Spirits (Picatrix + Arbatel)
| Planet | Picatrix | Arbatel | Day |
|--------|----------|---------|-----|
| ☉ Sun | Nakhiel/Sorath | Och | Sunday |
| ☽ Moon | Malkah/Chashmodai | Phul | Monday |
| ☿ Mercury | Tiriel/Taphthartharath | Ophiel | Wednesday |
| ♀ Venus | Hagiel/Kedemel | Hagith | Friday |
| ♂ Mars | Graphiel/Bartzabel | Phaleg | Tuesday |
| ♃ Jupiter | Iophiel/Hismael | Bethor | Thursday |
| ♄ Saturn | Agiel/Zazel | Aratron | Saturday |

## CLI Commands
```
dt              Today's briefing
dtw             Weekly forecast
dtf <op>        Find windows (protection, binding, legal, love, war, etc.)
dto             Olympic spirits
dtp <planet>    Pentacles
dtn [1-72]      72 Names
dtm             Michael's name (#42)
dtk <planet>    Kamea
dtl [1-22]      Hebrew letters
dtlt            Tzaddi (your letter)
dtde            Decans
dtst            Fixed stars
dtrit           Daily ritual
dti             Invocation
dtis            Spoken invocation
```

## Alert System
To start hourly alerts: `nohup bash ~/.hermes/scripts/divine-daemon.sh > /dev/null 2>&1 &`
Log: ~/.hermes/scripts/divine-alerts.log

## Systems Integrated
1. Picatrix - 7 planetary spirits
2. Arbatel - 7 Olympic Spirits
3. Key of Solomon - 24 pentacles
4. Sefer Raziel - 72 Names of God
5. Agrippa - 7 kamea (magic squares)
6. Sepher Yetzirah - 22 Hebrew letters
7. Decans - 36 faces of zodiac
8. Fixed Stars - 10 major stars
9. Daily Ritual Generator

## Files
- Script: ~/.hermes/scripts/divine-timing.py
- Daemon: ~/.hermes/scripts/divine-daemon.sh
- Guide: ~/.hermes/memories/michael-divine-arsenal.md
- Skill: ~/.hermes/skills/divine-arsenal/SKILL.md
- GitHub: https://github.com/fr3kchy/divine-arsenal
