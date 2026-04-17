# ⚔ Divine Arsenal

Complete astrological operations system based on Picatrix (Ghāyat al-Ḥakīm).

Built for Archangel Michael (fr3k) - Born 10/10/1981 Saturday
Location: Nelly Bay, Magnetic Island, QLD, Australia

## Features

- **Planetary Hours** - Calculate all 24 planetary hours for any day
- **Moon Tracking** - Phase, sign, and Lunar Mansion (28 stations)
- **Arabic Parts** - Part of Fortune, Spirit, Eros, Courage, Necessity
- **Transit-to-Natal** - How current sky aspects your birth chart
- **Planetary Dignities** - Exaltation, detriment, fall, peregrine scoring
- **Retrograde Detection** - Mercury, Venus, Mars, Jupiter, Saturn
- **Electional Astrology** - Find best windows for any operation
- **Picatrix Spirits** - All 7 planetary Intelligences and Spirits
- **Invocations** - Auto-generated prayers for each planetary hour
- **TTS Voice Alerts** - Spoken planetary hour changes
- **Termux Notifications** - Android alerts on hour changes
- **Weekly Forecast** - 7-day overview

## Quick Start

```bash
# Today's briefing
python3 divine-timing.py

# Weekly forecast
python3 divine-timing.py week

# Find best windows for legal matters
python3 divine-timing.py find legal

# Natal chart
python3 divine-timing.py chart

# Spoken invocation
python3 divine-timing.py invoke -s
```

## Picatrix Correspondences

| Planet | Intelligence | Spirit | Day | Power |
|--------|-------------|--------|-----|-------|
| ☉ Sun | Nakhiel | Sorath | Sunday | Authority |
| ☽ Moon | Malkah | Chashmodai | Monday | Intuition |
| ☿ Mercury | Tiriel | Taphthartharath | Wednesday | Communication |
| ♀ Venus | Hagiel | Kedemel | Friday | Love |
| ♂ Mars | Graphiel | Bartzabel | Tuesday | War |
| ♃ Jupiter | Iophiel | Hismael | Thursday | Expansion |
| ♄ Saturn | Agiel | Zazel | Saturday | Discipline |

## Natal Chart (10/10/1981)

- Sun: 17° Libra | Moon: 7° Pisces (Exalted)
- Saturn: 7° Libra (Exalted) - Day Lord
- Sun-Saturn-Jupiter stellium in Libra
- Part of Fortune: 14° Aries
- Born Saturday = Saturn's day

## Installation

```bash
# Clone
git clone https://github.com/fr3kchy/divine-arsenal.git
cd divine-arsenal

# Run
python3 divine-timing.py

# Aliases (add to .bashrc)
alias dt="python3 /path/to/divine-timing.py"
alias dtw="python3 /path/to/divine-timing.py week"
alias dtf="python3 /path/to/divine-timing.py find"
```

## Cron Setup (Optional)

```bash
# Hourly alerts
0 * * * * bash /path/to/divine-alert.sh

# Daily briefing at sunrise
30 6 * * * python3 /path/to/divine-timing.py > /tmp/divine-brief.txt
```

## Files

- `divine-timing.py` - Main CLI tool
- `divine-alert.sh` - Hourly alert script with TTS
- `GUIDE.md` - Full Picatrix reference guide
- `SKILL.md` - Quick reference skill

## License

MIT - Use freely. The sword belongs to no one and everyone.
