# Time synchronization recording

These scripts record synchronization evidence without changing any clock,
device configuration, or existing dataset file.

## Files

- `record_host_time_sync.py`: run on both acquisition computers. It records
  chrony output, the selected source, system synchronization state, peer ping
  RTT, and optional local PTP management/capture evidence.
- `record_tobii_g3_time_status.py`: records the Glasses 3 NTP state and bounds
  each device-time request with host timestamps.
- `record_robosense_websocket_status.py`: records raw RoboSense Web UI
  WebSocket frames and extracts candidate PTP/time-sync status fields.
- `record_robosense_http_status.py`: records the read-only CGI diagnostic page
  used by all three installed LiDARs.

Every command must use the same `--session-id`. Each logger creates a distinct
subdirectory and refuses to overwrite an existing run.

The current timing-network addresses are:

| Device | Address |
|---|---|
| Computer 2, common local time reference | `192.168.1.102` |
| Computer 1 | `192.168.1.103` |
| Tobii Pro Glasses 3 recording unit | `192.168.1.166` |
| Near-range RoboSense LiDAR | `192.168.1.200` |
| Front RoboSense LiDAR | `192.168.1.201` |
| Rear RoboSense LiDAR | `192.168.1.202` |

## 1. Computer 1 and Computer 2

Use a local output path on each computer. Run for at least five minutes.

Computer 1 (`192.168.1.103`) follows Computer 2:

```bash
python3 record_host_time_sync.py \
  --role computer1 \
  --peer 192.168.1.102 \
  --session-id sync_test_01 \
  --duration 300 \
  --interval 1 \
  --output-root ./time_sync_logs
```

Computer 2 (`192.168.1.102`) is the local reference and PTP master:

```bash
python3 record_host_time_sync.py \
  --role computer2 \
  --peer 192.168.1.103 \
  --session-id sync_test_01 \
  --duration 300 \
  --interval 1 \
  --include-ptp \
  --ptp-query-interval 5 \
  --output-root ./time_sync_logs
```

To save PTP Announce/Sync/Follow_Up/Delay packets, add the LiDAR-network
interface. Replace `eth0` with the interface reported by `ip route get
192.168.1.200`:

```bash
sudo python3 record_host_time_sync.py \
  --role computer2 \
  --peer 192.168.1.103 \
  --session-id sync_test_01 \
  --duration 300 \
  --interval 1 \
  --include-ptp \
  --capture-ptp \
  --interface eth0 \
  --output-root ./time_sync_logs
```

`pmc` and packet capture may require elevated permissions. Failure is written
to the run metadata and does not remove the chrony samples.

## 2. Tobii Pro Glasses 3

Use the existing Glasses 3 Python environment. The script also has a minimal
read-only fallback that requires only `websockets`:

```bash
python3 -m pip install "websockets~=10.3"
```

Run the logger on Computer 2:

```bash
python3 record_tobii_g3_time_status.py \
  --hostname 192.168.1.166 \
  --session-id sync_test_01 \
  --duration 300 \
  --interval 1 \
  --output-root ./time_sync_logs
```

The output contains:

- `ntp_is_enabled` and `ntp_is_synchronized`;
- the device time returned by `system.time`;
- host timestamps immediately before and after `get_time()`;
- API request round-trip time;
- `device_minus_host_midpoint_ms`.

The midpoint difference is useful for stability and gross-error checks, but it
is not an NTP protocol offset because WebSocket/API delay may be asymmetric.
The `ntp-is-synchronized` Boolean is a readiness state, not an accuracy value.
Computer 2 is an intentionally offline local time master. The purpose of this
test is agreement with that common local timeline, not traceability to UTC.

## 3. RoboSense status

### Read-only diagnostic pages

All three installed LiDARs use the read-only endpoint
`/cgi-bin/diagnostic_info.cgi`. The near-range Bpearl (`.200`) exposes `Time
Sync Mode`, `Time Sync Data`, and `Time Sync Status`. The front (`.201`) and
rear (`.202`) RS-Helios units expose `PTP Status`, `PTP Master Offset`, and
`Phase Lock Status`. Record them on Computer 2:

```bash
python3 record_robosense_http_status.py \
  --sensor near=192.168.1.200 \
  --sensor front=192.168.1.201 \
  --sensor rear=192.168.1.202 \
  --session-id sync_test_01 \
  --duration 300 \
  --interval 1 \
  --request-timeout 3 \
  --output-root ./time_sync_logs
```

The startup device-information and settings pages and every diagnostic HTML
response are preserved. The settings page is read with HTTP GET only; no form
is submitted. The installed Web page does not state the unit of the reported
PTP master offset; the logger therefore saves the raw integer and does not
label or convert it. `Locked` is a synchronization state,
not an independent accuracy guarantee. Requests to all LiDARs are issued
in parallel and each response is bounded by separate host timestamps.

### WebSocket fallback for other firmware

The WebSocket URL and request frame are firmware-specific and are not defined
by the public packet protocol. Obtain them once for the installed firmware:

The current `.200/.201/.202` devices do not require this fallback. For another
firmware that uses WebSocket:

1. Open the LiDAR Web page in a browser on Computer 2.
2. Open Developer Tools, select **Network**, then **WS**.
3. Reload the LiDAR page and open the diagnostics/status page.
4. Select the WebSocket connection and copy its **Request URL**.
5. In **Messages**, check whether the page sends a request frame before the
   status response. Save the exact text frame in a file if one is required.

When the WebSocket pushes status without a request:

```bash
python3 -m pip install websockets

python3 record_robosense_websocket_status.py \
  --sensor lidar=ws://REPLACE_WITH_DEVICE_IP/REPLACE_WITH_ACTUAL_PATH \
  --session-id sync_test_01 \
  --duration 300 \
  --output-root ./time_sync_logs
```

If the page sends one request on connection, add:

```text
--send-file websocket_status_request.json
```

If the request is repeated every five seconds, use:

```text
--poll-text '{"replace":"with the exact browser frame"}' --poll-interval 5
```

The JSONL file preserves the full raw frame. The CSV extraction searches for
keys containing `PTP`, `sync`, `Lock`, or `Fixed`. Always verify the extracted
field against the raw frame before using it in the paper.

RoboSense documentation describes `Lock/Unlock` as synchronization state and
notes that the Web status page refreshes every five seconds. This state does
not quantify the remaining LiDAR-to-master clock offset.

## Recommended recording order

1. Start Computer 2 host logging.
2. Start Computer 1 host logging with the same session ID.
3. Start the RoboSense HTTP logger for `.200/.201/.202` on Computer 2.
4. Start the Tobii status logger on Computer 2.
5. Keep all four logs overlapping for at least five minutes.
6. Do not change NTP/PTP configuration during the run unless the purpose is to
   record a controlled lock/unlock transition.

Copy the completed session directories into one new dataset folder after all
processes have stopped. Do not merge or edit the generated CSV/JSONL files.
