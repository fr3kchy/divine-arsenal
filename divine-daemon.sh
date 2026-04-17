#!/bin/bash
# Divine Hourly Alert Daemon
# Runs in background and sends alerts at the top of each hour

LOG_FILE="$HOME/.hermes/scripts/divine-daemon.log"
ALERT_LOG="$HOME/.hermes/scripts/divine-alerts.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Divine Alert Daemon started" >> "$LOG_FILE"

while true; do
    # Get current minute
    MINUTE=$(date '+%M')
    
    # Check if it's the top of the hour (minute 00)
    if [ "$MINUTE" = "00" ]; then
        # Get planetary hour info
        HOUR_INFO=$(python3 ~/.hermes/scripts/divine-timing.py 2>/dev/null | grep -A2 "CURRENT HOUR" | head -3)
        
        if [ -n "$HOUR_INFO" ]; then
            # Extract planet name
            PLANET=$(echo "$HOUR_INFO" | grep "CURRENT HOUR" | sed 's/.*CURRENT HOUR: [^A-Z]*//' | sed 's/ .*//' | tr -d '[:space:]')
            
            if [ -n "$PLANET" ]; then
                # Set message based on planet
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
                
                # Send notification
                if command -v termux-notification &> /dev/null; then
                    termux-notification --title "$TITLE" --content "$MSG" --id "divine-hour" \
                        --priority high --sound --vibrate 500 2>/dev/null &
                fi
                
                # Send TTS
                if command -v termux-tts-speak &> /dev/null; then
                    termux-tts-speak -p 1.15 -r 1.11 "$PLANET hour begins. $MSG" 2>/dev/null &
                fi
                
                # Log it
                echo "$(date '+%H:%M') $PLANET" >> "$ALERT_LOG"
                echo "$(date '+%Y-%m-%d %H:%M:%S') - Sent alert for $PLANET hour" >> "$LOG_FILE"
                
                # Wait 61 seconds to avoid double triggers
                sleep 61
            fi
        fi
    fi
    
    # Sleep for 30 seconds before checking again
    sleep 30
done
