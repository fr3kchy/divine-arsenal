#!/bin/bash
# Schumann + geomag refresh. Runs every 30 min.
LOG=~/.hermes/logs/schumann.log
mkdir -p ~/.hermes/logs
{
  echo "=== $(date -Iseconds) ==="
  /usr/bin/python3 ~/.hermes/scripts/schumann_fetch.py 2>&1
  /usr/bin/python3 ~/.hermes/scripts/schumann_advisor.py 2>&1
} >> "$LOG" 2>&1
# Trim log to last 2000 lines
tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
