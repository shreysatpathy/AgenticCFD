#!/bin/bash
LOG_FILE="thermal_simulation.log"
while [ ! -f "$LOG_FILE" ]; do sleep 1; done

echo "📊 Monitoring simulation progress..."
tail -f "$LOG_FILE" | while read line; do
    if [[ "$line" =~ Time\ =\ ([0-9.]+)s ]]; then
        TIME=${BASH_REMATCH[1]}
        echo "⏱️  Time: ${TIME}s"
    elif [[ "$line" =~ "Solving for T" ]]; then
        echo "🌡️  Temperature solving..."
    elif [[ "$line" =~ "FOAM FATAL" ]]; then
        echo "❌ Fatal error detected!"
        break
    fi
done
