#!/usr/bin/env bash

MAX_OFFSET_SEC=0.001

TRACKING_OUTPUT=$(chronyc tracking 2>/dev/null)
OFFSET_LINE=$(printf '%s\n' "$TRACKING_OUTPUT" | grep "System time" | sed 's/^[^:]*: *//')
OFFSET_SEC=$(printf '%s\n' "$OFFSET_LINE" | grep -oE '[0-9]+(\.[0-9]+)?' | head -n1)

SYNC_OK=false

if [ -n "$OFFSET_SEC" ]; then
    if awk "BEGIN {exit !($OFFSET_SEC < $MAX_OFFSET_SEC)}"; then
        SYNC_OK=true
    fi
fi

echo "NTP sync: $SYNC_OK"
echo "Offset: $OFFSET_LINE"

if [ "$SYNC_OK" != "true" ]; then
    exit 0
fi

if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux not found"
    exit 1
fi

SESSION="bikelab_interfaces1"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "tmux session already exists"
    exit 0
fi

tmux new-session -d -s "$SESSION" -n gps

tmux send-keys -t "$SESSION:0.0" \
  "ros2 launch ublox_dgnss ublox_rover_hpposllh_navsatfix.launch.py" C-m

tmux split-window -v -t "$SESSION:0"

tmux send-keys -t "$SESSION:0.1" \
  "ros2 launch ublox_dgnss ntrip_client_cli.launch.py" C-m

tmux select-layout -t "$SESSION:0" even-vertical

echo "GPS started"
echo "tmux attach -t $SESSION"
