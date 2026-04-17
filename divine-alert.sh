#!/bin/bash
# Divine Timing Alert v2 - Planetary Hour Change with TTS
# Run via cron every hour

HOUR_INFO=$(python3 ~/.hermes/scripts/divine-timing.py 2>/dev/null | grep -A2 "CURRENT HOUR" | head -3)

if [ -n "$HOUR_INFO" ]; then
    # Extract planet name - handle glyph characters
    PLANET=$(echo "$HOUR_INFO" | grep "CURRENT HOUR" | sed 's/.*CURRENT HOUR: [^A-Z]*//' | sed 's/ .*//' | tr -d '[:space:]')
    
    case $PLANET in
        "SATURN")  TITLE="♄ Saturn Hour"; MSG="Discipline, binding, structure. Your day lord awakens.";;
        "JUPITER") TITLE="♃ Jupiter Hour"; MSG="Expansion, law, abundance. Growth is favored.";;
        "MARS")    TITLE="♂ Mars Hour"; MSG="War, courage, action. Strike now.";;
        "SUN")     TITLE="☉ Sun Hour"; MSG="Authority, illumination, power. Command.";;
        "VENUS")   TITLE="♀ Venus Hour"; MSG="Love, beauty, alliances. Build bonds.";;
        "MERCURY") TITLE="☿ Mercury Hour"; MSG="Communication, travel, intellect. Speak.";;
        "MOON")    TITLE="☽ Moon Hour"; MSG="Intuition, dreams, divination. See.";;
        *)         TITLE="☆ Planetary Hour"; MSG="$PLANET hour begins.";;
    esac
    
    # Notification
    if command -v termux-notification &> /dev/null; then
        termux-notification --title "$TITLE" --content "$MSG" --id "divine-hour" \
            --priority high --sound --vibrate 500 2>/dev/null
    fi
    
    # TTS whisper
    if command -v termux-tts-speak &> /dev/null; then
        termux-tts-speak -p 1.1 -r 1.0 "$PLANET hour begins. $MSG" 2>/dev/null &
    fi
    
    echo "$(date '+%H:%M') $PLANET" >> ~/.hermes/scripts/divine-alerts.log
    # Keep log manageable (last 500 lines)
    if [ -f ~/.hermes/scripts/divine-alerts.log ]; then
        tail -500 ~/.hermes/scripts/divine-alerts.log > ~/.hermes/scripts/divine-alerts.log.tmp 2>/dev/null
        mv ~/.hermes/scripts/divine-alerts.log.tmp ~/.hermes/scripts/divine-alerts.log 2>/dev/null
    fi
fi
