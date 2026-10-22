#!/usr/bin/env bash

# ---------------------------
# 1) PTP masters and NTP server check
# ---------------------------


NTP_OK=false

# 1) GM master check
echo
echo "# 1) PTP GM check (pmc GET PORT_DATA_SET)"
echo "#    true  = portState MASTER (this computer is acting as PTP Grandmaster)"
echo "#    false = not MASTER (this computer is not the GM)"
sudo pmc -u -b 0 "GET PORT_DATA_SET" 2>/dev/null | grep -q "portState[[:space:]]*MASTER" && echo true || echo false

# 2) NTP server check
if ss -lun 2>/dev/null | grep -qE '[:.]123[[:space:]]'; then
    NTP_OK=true
fi

echo "#2) NTP server: $NTP_OK"
# ---------------------------
# 2) Eyetracker NTP sync check
# ---------------------------
echo "#3) Eyetracker NTP sync check (HTTP endpoint):"
echo "#    true  = endpoint indicates synchronized"
echo "#    false = endpoint indicates NOT synchronized, or request failed"

eye_resp="$(curl -fsS --max-time 2 "http://192.168.1.166/rest/system.ntp-is-synchronized" 2>/dev/null || true)"

# Try to interpret common responses: true/false, 1/0, JSON containing "true"/"false"
eye_ok="false"
if echo "$eye_resp" | grep -qiE 'true|1'; then
  eye_ok="true"
elif echo "$eye_resp" | grep -qiE 'false|0'; then
  eye_ok="false"
else
  eye_ok="false"
fi

echo "$eye_ok"
echo "#    raw response: ${eye_resp:-<empty/no response>}"

echo


