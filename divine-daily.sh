#!/bin/bash
# Divine Daily Briefing - Runs every morning at sunrise
# Sends notification with today's key info

# Get today's data
TODAY=$(date '+%Y-%m-%d')
OUTPUT=$(python3 ~/.hermes/scripts/divine-timing.py 2>/dev/null)

# Extract key info
DAY_LORD=$(echo "$OUTPUT" | grep "Day Lord:" | head -1 | grep -oP '(?<=: )\w+')
MOON_INFO=$(echo "$OUTPUT" | grep "MOON" | head -1)
CURRENT_HOUR=$(echo "$OUTPUT" | grep "CURRENT HOUR" | head -1)
POWER_WINDOWS=$(echo "$OUTPUT" | grep -A5 "POWER WINDOWS TONIGHT" | tail -5)

# Planet emojis/symbols
case $DAY_LORD in
    "SATURN")   SYMBOL="♄";;
    "JUPITER")  SYMBOL="♃";;
    "MARS")     SYMBOL="♂";;
    "SUN")      SYMBOL="☉";;
    "VENUS")    SYMBOL="♀";;
    "MERCURY")  SYMBOL="☿";;
    "MOON")     SYMBOL="☽";;
    *)          SYMBOL="☆";;
esac

# Build notification content
TITLE="$SYMBOL $DAY_LORD's Day - Divine Timing"

# Get power windows as single line
WINDOWS=$(echo "$POWER_WINDOWS" | tr '\n' ' ' | sed 's/  */ /g')

# Send notification
if command -v termux-notification &> /dev/null; then
    termux-notification \
        --title "$TITLE" \
        --content "Today: $DAY_LORD governs. $MOON_INFO. Power windows tonight: check divine-timing.py" \
        --id "divine-daily" \
        --priority high \
        --sound \
        --vibrate 1000 \
        --button1 "Full Briefing" \
        --button1-action "termux-toast 'Run: python3 ~/.hermes/scripts/divine-timing.py'" \
        2>/dev/null
fi

# Also send to terminal if running interactively
if [ -t 1 ]; then
    echo "$OUTPUT"
fi

# Log it
echo "$(date '+%Y-%m-%d %H:%M') - Daily briefing sent: $DAY_LORD's day" >> ~/.hermes/scripts/divine-briefings.log
