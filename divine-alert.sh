#!/bin/bash
# Divine Timing Alert v2 - Planetary Hour Change with TTS
# Run via cron every hour

HOUR_INFO=$(python3 ~/scripts/divine-timing.py 2>/dev/null | grep -A2 "CURRENT HOUR" | head -3)

if [ -n "$HOUR_INFO" ]; then
    PLANET=$(echo "$HOUR_INFO" | grep -oP '(?<=CURRENT HOUR: )\w+')
    
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
    
    echo "$(date '+%H:%M') $PLANET" >> ~/scripts/divine-alerts.log
    tail -500 ~/scripts/divine-alerts.log > /tmp/dal.tmp && mv /tmp/dal.tmp ~/scripts/divine-alerts.log
fi
