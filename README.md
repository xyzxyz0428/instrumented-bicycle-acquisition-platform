# Instrumented Bicycle Multi-Sensor Acquisition Platform

This repository contains the synchronized acquisition software and field protocol for an instrumented bicycle. The platform records RTK GNSS, IMU, steering input, bilateral brake force, ANT+ wheel speed and power, rider-view video, Tobii Pro Glasses 3 data, and three RoboSense LiDAR streams across two Raspberry Pi acquisition computers.

## Authorship

The instrumented-bicycle recording platform, system integration, original acquisition utilities, and this protocol were developed and are maintained by **Xinyu Zhang**.

Copyright © 2025–2026 Xinyu Zhang. Copyright ownership and authorship are not transferred by the open-source licence. Third-party components remain the property of their respective copyright holders; see [Copyright and licensing](#copyright-and-licensing).

## Repository layout

The acquisition software is separated by deployment computer:

```text
.
├── bikelab_interfaces1/    # Computer 1: GNSS, IMU, steering, brakes, ANT+, ROS 2 bag
└── bikelab_interfaces2/    # Computer 2: camera, Tobii controller, and three LiDARs
```

Each directory is self-contained at the relative path expected by that computer's unchanged startup scripts. The root directory contains only repository-level documentation, licensing, and ignore rules in addition to these two deployment directories.

## Deployment layout

Clone the unified repository outside the ROS 2 workspace on each computer, then link only that computer's deployment directory into the historical path expected by the unchanged scripts. This prevents ROS 2 from discovering the other computer's packages.

| Computer | Required checkout path |
| --- | --- |
| Computer 1 | `~/ros2_ws/src/bikelab_interfaces1` |
| Computer 2 | `~/ros2_ws/src/bikelab_interfaces2` (`/home/ubuntu/ros2_ws/src/bikelab_interfaces2`) |

If either target path already exists, preserve any local changes and move the existing checkout aside before continuing. The commands below deliberately fail instead of overwriting an existing directory or link.

```bash
# Computer 1
git clone https://github.com/xyzxyz0428/instrumented-bicycle-acquisition-platform.git \
  ~/instrumented-bicycle-acquisition-platform
test ! -e ~/ros2_ws/src/bikelab_interfaces1 && \
  ln -sT ~/instrumented-bicycle-acquisition-platform/bikelab_interfaces1 \
    ~/ros2_ws/src/bikelab_interfaces1

# Computer 2
git clone https://github.com/xyzxyz0428/instrumented-bicycle-acquisition-platform.git \
  ~/instrumented-bicycle-acquisition-platform
test ! -e ~/ros2_ws/src/bikelab_interfaces2 && \
  ln -sT ~/instrumented-bicycle-acquisition-platform/bikelab_interfaces2 \
    ~/ros2_ws/src/bikelab_interfaces2
```

After deployment, the operational commands remain unchanged:

```bash
cd ~/ros2_ws/src/bikelab_interfaces1       # Computer 1
cd ~/ros2_ws/src/bikelab_interfaces2       # Computer 2 (ubuntu account)
```

### Install the external Tobii dependency on Computer 2

This repository follows a non-redistribution model for the Tobii dependency: it contains neither the `glasses3-pylib` source nor the locally modified deployment copy. Each user obtains the dependency independently and directly from Tobii.

Use this pinned official upstream reference:

```text
Tobii glasses3-pylib commit: 5868e2d327a077cb6bbe276182188b81fc90f224
```

Install it directly from Tobii, then link the Xinyu Zhang recording controller into the location expected by the unchanged startup script:

```bash
cd /home/ubuntu/ros2_ws/src/bikelab_interfaces2

git clone https://github.com/tobii/glasses3-pylib.git glasses3-pylib
git -C glasses3-pylib checkout --detach \
  5868e2d327a077cb6bbe276182188b81fc90f224

/home/ubuntu/.pyenv/versions/g3env/bin/python -m pip install \
  ./glasses3-pylib python-dotenv

test ! -e glasses3-pylib/tests/save_record.py
ln -s ../../tobii_tools/save_record.py \
  glasses3-pylib/tests/save_record.py
```

Verify the exact checkout, clean worktree, controller link, controller checksum, and import:

```bash
test "$(git -C glasses3-pylib rev-parse HEAD)" = \
  "5868e2d327a077cb6bbe276182188b81fc90f224"
git -C glasses3-pylib diff --quiet
test "$(sha256sum tobii_tools/save_record.py | cut -d ' ' -f1)" = \
  "870700879caf879b51ebc80d5b6404eeb8fa6069f07880654547857474c8e057"
test "$(readlink -f glasses3-pylib/tests/save_record.py)" = \
  "$(readlink -f tobii_tools/save_record.py)"
/home/ubuntu/.pyenv/versions/g3env/bin/python -c \
  "from g3pylib import connect_to_glasses; print('g3pylib import: OK')"
```

The expected SHA-256 for `tobii_tools/save_record.py` is:

```text
870700879caf879b51ebc80d5b6404eeb8fa6069f07880654547857474c8e057
```

The closest identified official upstream revision is `5868e2d327a077cb6bbe276182188b81fc90f224`. It is not a byte-identical copy of the field-deployed library. The deployed copy disabled the PyAV dependency and made the `Streams` import optional; those Tobii-derived changes are intentionally not redistributed. Treat this commit as a separately obtained replacement dependency, not an exact archive of the acquisition environment. Before formal acquisition, validate it on Computer 2 with a complete short recording and record the OS, architecture, Python version, and `python -m pip freeze --all` output in the dataset manifest.

Do not commit the cloned `glasses3-pylib/` directory. It is excluded by the root `.gitignore` and remains governed by Tobii's licence.

## Network and synchronization roles

The field network uses `192.168.1.0/24`.

| Device | IPv4 address | Required clock state |
| --- | --- | --- |
| Operator computer | `192.168.1.104` | Static wired address |
| Computer 1 | `192.168.1.103` | Chrony system-time correction magnitude below `1 ms`; deployment target is Computer 2's local reference |
| Computer 2 | `192.168.1.102` | Local time reference, UDP/123 NTP service listening, and PTP port in `MASTER` state |
| Tobii Pro Glasses 3 | `192.168.1.166` | `ntp-is-synchronized = true` |
| Near-range LiDAR | `192.168.1.200` | Web diagnostics report locked time synchronization |
| Front LiDAR | `192.168.1.201` | Web diagnostics report locked time synchronization |
| Rear LiDAR | `192.168.1.202` | Web diagnostics report locked time synchronization |

Do not start an experimental run while a required state is false or unlocked. The startup checks are operator gates: some scripts return exit status `0` after printing a failed readiness result, so always inspect their output.

## Deployment-specific constants

| Component | Current deployed value |
| --- | --- |
| Wheel circumference | `2.20114 m` |
| ANT+ wheel-speed device ID | `18412` |
| ANT+ power-meter device ID | `64434` |
| IMU serial device | `/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_0003-if00-port0` |
| IMU serial rate | `115200 baud` |
| Steering calibration | ADC `724`, `529`, and `334` correspond to `-45°`, `0°`, and `+45°`; nominal sampling rate `10 Hz` |
| Brake sensors | Left register `0x17`; right register `0x14`; nominal sampling rate `10 Hz` |
| Brake-force calibration | Left: `force_g = 5.9092229449 × ADC − 321.9034713174`; right: `force_g = 6.9068825517 × ADC − 341.0880127929` |
| Computer 2 network interface | `eth0` |
| Camera | `/dev/video0`; nominally `1280 × 720` at `30 frames/s`, MJPEG |
| Tobii Pro Glasses 3 | `192.168.1.166`; Python at `/home/ubuntu/.pyenv/versions/g3env/bin/python` |
| LiDAR `.200` | `RSBP`; UDP ports `2000/2001` |
| LiDAR `.201` | `RSHELIOS`; UDP ports `2010/2011` |
| LiDAR `.202` | `RSHELIOS`; UDP ports `2020/2021` |

Record any approved change to these constants in the dataset manifest and release notes.

## Before each recording

Confirm that:

- the operator computer uses `192.168.1.104/24` on the wired interface;
- both Raspberry Pi computers and all non-Tobii sensors are powered and reachable; keep the Tobii Recording Unit switched off until Step 2 is complete;
- at the recording site, Computer 2 is manually set to the actual current local date and time before every recording session and before it serves as the NTP/PTP reference;
- the ROS 2 environment is sourced on both computers;
- the repository and Tobii dependency are deployed at the exact paths above;
- `~/bikelab_interface_logs` already exists and is writable on Computer 1;
- `/mnt/bikelab_data` is mounted and writable on Computer 2;
- both computers have sufficient free storage;
- Computer 1 can reach the configured NTRIP service; and
- participant consent, ethics approval, and the study privacy procedure cover video and eye-tracking acquisition.

Never commit Wi-Fi, NTRIP, or participant credentials. Useful `tmux` controls are `Ctrl-b`, then `o` to change pane, and `Ctrl-b`, then `d` to detach. See the [tmux cheat sheet](https://tmuxcheatsheet.com/) for additional commands.

## Recording procedure

### 1. Connect from the operator computer

Set the operator computer's wired IPv4 address to `192.168.1.104/24`, then open one SSH session to each acquisition computer:

```bash
ssh bikelab@192.168.1.103
ssh ubuntu@192.168.1.102
```

Computer 1 uses the `bikelab` account. Computer 2 must use the `ubuntu` account because its startup script contains `/home/ubuntu/...` paths.

### 2. Establish the time reference and network access

On **Computer 2**, manually set the system clock at the recording site at the start of **every recording session**. Replace the placeholder with the actual current local date and time:

```bash
sudo date -s "YYYY-MM-DD HH:MM:SS"
timedatectl status
date --iso-8601=seconds
date -u --iso-8601=seconds
```

Confirm the configured timezone, UTC offset, local timestamp, and UTC timestamp immediately. Do not reuse the time from a previous session. Then confirm that the NTP and PTP services configured for the deployment are running.

On **Computer 1**, connect to the Wi-Fi network used for NTRIP/internet access, then inspect the active Chrony source:

```bash
sudo nmcli device wifi connect "WIFI_NAME" password "PASSWORD"
chronyc sources -v
chronyc tracking
```

Confirm that the intended reference is selected. The startup script checks only the magnitude of Chrony's reported system-time correction; it does not prove the identity of the selected source.

Only after the network connection, Computer 2 time reference, NTP/PTP services, and Computer 1 clock synchronization have all been confirmed as normal should the operator switch on the **Tobii Pro Glasses 3 Recording Unit**. Do not power on the Recording Unit before these checks pass.

### 3. Start recording on Computer 1

#### 3.1 Check time synchronization and start GNSS/NTRIP

```bash
cd ~/ros2_ws/src/bikelab_interfaces1
./check_syn_start_gps.sh
tmux attach -t bikelab_interfaces1
```

For a new session, proceed only when the script prints `NTP sync: true`, with an absolute offset below `0.001 s`, followed by `GPS started`. If it prints `false`, it does not create the tmux session but currently exits with status `0`; treat the printed result as authoritative. If `bikelab_interfaces1` already exists, the script prints `tmux session already exists` and starts nothing new. Attach to it, confirm that both panes belong to the current run, and remove any stale session before retrying.

In the `gps` tmux window, confirm that:

- `ublox_rover_hpposllh_navsatfix.launch.py` is running and publishing GNSS data; and
- `ntrip_client_cli.launch.py` starts without error and receives corrections.

Detach with `Ctrl-b`, then `d`. Perform the receiver's initialization ride, including changes in direction and turns, and wait for the RTK state required by the study.

#### 3.2 Start the Computer 1 sensor loggers

```bash
cd ~/ros2_ws/src/bikelab_interfaces1
./start_recording.sh
tmux attach -t bikelab_interfaces1
```

The script reads one `/ubx_nav_pvt` message with a three-second timeout. It proceeds only when `carr_soln.status` is non-zero and `diff_soln=1`. This accepts RTK float or fixed; apply any stricter study-specific requirement manually.

If the `sensors` tmux window already exists, the script starts no new logger. Inspect every existing pane and remove a stale window before retrying.

Confirm active output in all four panes:

- steering-angle potentiometer;
- combined ANT+ wheel-speed and power logger;
- IMU logger; and
- left/right brake-force logger.

Check for new samples and the absence of repeated I/O, serial, CRC, or device-not-found errors. Detach with `Ctrl-b`, then `d`.

#### 3.3 Start the ROS 2 bag

`start_recording.sh` does not start a ROS 2 bag. In a separate Computer 1 terminal, run:

```bash
cd ~/bikelab_interface_logs
ros2 bag record -a
```

Leave this command running for the full experimental run.

### 4. Start recording on Computer 2

#### 4.1 Verify PTP, NTP service, eye-tracker NTP, and LiDAR synchronization

```bash
cd /home/ubuntu/ros2_ws/src/bikelab_interfaces2
./check_ptp_eye_lidar.sh
```

The required results are:

```text
# 1) PTP GM check (pmc GET PORT_DATA_SET)
true
#2) NTP server: true
#3) Eyetracker NTP sync check (HTTP endpoint):
true
```

The PTP result must show that Computer 2 is `MASTER`. The NTP server check confirms only that a process is listening on UDP port 123. The eye-tracker result and its printed raw response must both unambiguously represent Boolean `true`; an empty or more complex raw response requires manual investigation because the current parser also matches the character `1`. The script does not fail solely because one of these Boolean checks is false, so inspect every line.

From the operator computer, open each diagnostic page and confirm that the time synchronization status is locked:

- [LiDAR 192.168.1.200](http://192.168.1.200/cgi-bin/diagnostic_info.cgi)
- [LiDAR 192.168.1.201](http://192.168.1.201/cgi-bin/diagnostic_info.cgi)
- [LiDAR 192.168.1.202](http://192.168.1.202/cgi-bin/diagnostic_info.cgi)

#### 4.2 Start camera, glasses, and LiDAR capture

```bash
cd /home/ubuntu/ros2_ws/src/bikelab_interfaces2
sudo -v
./start_camera_glass_lidar.sh
tmux attach -t bikelab_interfaces2
```

The `camera_glasses` window contains `CAM`, `G3`, and `PCAP` panes. In the `G3` pane:

1. place the Tobii calibration target approximately 50–100 cm in front of the participant;
2. follow the terminal prompt and press Enter to trigger calibration;
3. confirm `Calibration SUCCESS`; and
4. confirm both `recorder.start() returned: True` and `Received recorder started signal`.

If a `camera_glasses` window already exists, the startup script starts no new process. Confirm that all existing panes belong to the current run, or remove the stale window before retrying.

At connection, `save_record.py` checks the glasses clock. If the glasses are not synchronized, it attempts to enable NTP and waits up to 10 seconds. If synchronization still fails, it sets the glasses clock from Computer 2's current UTC clock before calibration. This is a clock-changing fallback; confirm that Computer 2 was set correctly, retain the terminal log, and do not proceed if the study protocol forbids this fallback.

Before riding, verify that:

- `CAM` reports its output directory and a stable capture rate;
- `G3` reports successful calibration and active recording; and
- `PCAP` reports that `tcpdump` is listening on `eth0` without error.

Do not rely only on the process exit status or a generic recording message: the current controller catches top-level exceptions without returning a non-zero exit code, and a missing start signal is not a hard gate. After installing or changing the Tobii dependency, complete a short end-to-end test (connect, synchronize, calibrate, start, stop with `Ctrl+C`), then confirm on the glasses that the test recording exists and can be exported.

Detach with `Ctrl-b`, then `d`.

## Record synchronization evidence for a publication run

The host-specific synchronization tools for [Computer 1](bikelab_interfaces1/time_sync_recording/README.md) and [Computer 2](bikelab_interfaces2/time_sync_recording/README.md) record read-only timing evidence for both hosts, Tobii Glasses 3, and all three LiDARs. For each formal validation run:

1. use the same `--session-id` for every logger;
2. start the Computer 2 host logger, then the Computer 1 host logger;
3. start the RoboSense HTTP and Tobii status loggers on Computer 2;
4. maintain at least five minutes of overlapping observations; and
5. copy the completed session directories into the dataset archive without editing their generated CSV or JSONL files.

The readiness Booleans and LiDAR `Locked` states do not by themselves quantify synchronization accuracy. Retain the raw timing evidence and request-bound timestamps supplied by these tools.

## Stop the recording safely

Always stop writers cleanly before shutting down a computer or removing storage.

### Computer 1

1. Stop the ROS 2 bag with `Ctrl+C` in its terminal. If that terminal is unavailable, send `SIGINT`:

   ```bash
   pkill -INT -f "ros2 bag record"
   ```

2. Wait for the bag writer to finish and return to the shell prompt.
3. Attach to the sensor session:

   ```bash
   tmux attach -t bikelab_interfaces1
   ```

4. Visit each active logger, GNSS, and NTRIP pane and press `Ctrl+C`. Wait for each process to stop and flush its output.
5. Remove the empty session only after every process has exited:

   ```bash
   tmux kill-session -t bikelab_interfaces1
   ```

### Computer 2

1. Attach to the session:

   ```bash
   tmux attach -t bikelab_interfaces2
   ```

2. In `G3`, press `Ctrl+C` first and wait for `Done. Recording stopped.`
3. In `PCAP`, press `Ctrl+C` and wait for the packet summary and shell prompt.
4. In `CAM`, press `Ctrl+C` and wait for the process to exit.
5. Remove the session only after all three processes have stopped:

   ```bash
   tmux kill-session -t bikelab_interfaces2
   ```

Do not use `tmux kill-session` as the first stop command. Premature termination can prevent the Tobii recorder, pcap writer, or camera writer from finalizing its output.

The current camera implementation does not explicitly call `VideoWriter.release()`. Before leaving the site, open the AVI and verify a plausible duration and frame count.

## Recorded outputs

### Computer 1

Outputs are stored under `~/bikelab_interface_logs/`:

| Pattern | Contents |
| --- | --- |
| `steering_angle_<timestamp>.csv` | Steering ADC values and interpolated steering angle |
| `brake_sensors_force_<timestamp>.csv` | Left/right brake ADC values and calibrated force in grams and newtons |
| `speed_decoded_<timestamp>.csv` | ANT+ wheel speed and distance |
| `speed_decoded_pages_<timestamp>.txt` | Optional observed ANT+ speed pages |
| `rally_payload_decoded_<timestamp>.csv` | ANT+ power-meter payload, cadence, power, and torque fields |
| `imu_<timestamp>.csv` | Raw and decoded IMU/AHRS data with integrity flags |
| `rosbag2_<timestamp>/` | ROS 2 bag created by `ros2 bag record -a` |

The deployed steering logger writes `angle_deg_clamped = NaN` for values strictly between `-45°` and `+45°`, and writes the interpolated/clamped value at or beyond those endpoints. Use `angle_deg` as the primary steering-angle field unless that behavior has been explicitly validated for the analysis. The brake-force logger clamps negative values from either linear calibration to `0 g`.

Timestamps in filenames are generated independently. Use the recorded Unix timestamps, not filename equality, for cross-sensor alignment.

### Computer 2

| Path | Contents |
| --- | --- |
| `/mnt/bikelab_data/camera_<YYYYMMDD_HHMMSS>/video_mjpg.avi` | USB-camera MJPEG video, nominally `1280 × 720` at `30 frames/s` |
| `/mnt/bikelab_data/camera_<YYYYMMDD_HHMMSS>/timestamps.csv` | Video frame index and Unix timestamp in nanoseconds |
| `/mnt/bikelab_data/rs_3lidars_<YYYYMMDD_HHMMSS>.pcap` | Raw UDP traffic from all three LiDAR units |
| Tobii Glasses 3 internal storage | Eye-tracking recording created by the glasses recorder |

The Computer 2 startup script neither downloads the Tobii recording nor creates a ROS 2 bag. Export the Tobii recording using the laboratory's validated procedure after the run.

Camera `timestamps.csv` values are Computer 2 host timestamps taken when the recorder writes the latest buffered frame; they are not hardware exposure timestamps. The fixed-rate writer may repeat the latest available frame or skip intermediate camera frames.

## Citation and archival release

For a publication release:

1. tag the exact unified repository commit used for acquisition;
2. archive that tag in a DOI-minting repository such as Zenodo;
3. add `CITATION.cff` after Xinyu Zhang's affiliation, ORCID, preferred software title, and DOI are verified;
4. cite the software DOI, dataset DOI, and associated article separately; and
5. ensure the archive is created from the tagged public repository revision.

Until a DOI is issued, cite the repository title, Xinyu Zhang, the exact commit hash, and the access date. See the [Scientific Data editorial policy](https://www.nature.com/sdata/policies/editorial-and-publishing-policies) and [repository guidance](https://www.nature.com/sdata/policies/repositories).

## Copyright and licensing

Copyright © 2025–2026 Xinyu Zhang.

Xinyu Zhang retains copyright and authorship in the original project software and documentation. Except where a file or directory carries a different notice, the original project material is released under the [Apache License 2.0](LICENSE). The licence grants reuse rights but does not transfer copyright ownership.

The repository contains RoboSense components under their included 3-clause BSD licences and ROS test templates under Apache-2.0. The CRC lookup tables in `bikelab_interfaces1/bikelab_interfaces/scripts/log_imu_to_csv.py` match material from an upstream repository that currently declares no licence; the root Apache licence therefore must not be read as granting rights in those tables. These tables are executed during the standard Computer 1 IMU recording path and therefore cannot be treated as unused code. Obtain written permission or a clear upstream licence before redistribution, or exclude/replace the affected material. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

The Tobii `glasses3-pylib` source, binaries, and locally modified deployment copy are not distributed by this repository. Each user must obtain the pinned dependency directly from the [official Tobii repository](https://github.com/tobii/glasses3-pylib) and accept the terms applicable to that download and use. Publishing or archiving this repository therefore does not redistribute the Tobii library. [`bikelab_interfaces2/tobii_tools/save_record.py`](bikelab_interfaces2/tobii_tools/save_record.py) was independently authored by Xinyu Zhang and is covered by Apache-2.0; no Tobii software is sublicensed through this project.

Apache-2.0 preserves Xinyu Zhang's copyright and attribution, but it also permits commercial use, modification, and redistribution subject to its terms. If the intended policy is to prohibit those uses, do not publish under Apache-2.0 until an appropriate alternative has been selected with institutional or legal review.

Research data are not covered by the software licence. A public dataset release should carry its own explicit licence, normally [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) when the depositor has authority to grant those rights. Identifiable video and eye-tracking data may be released only when participant consent, ethics approval, privacy law, and applicable third-party terms permit it; otherwise use an appropriate controlled-access repository and describe the access procedure in the article.

## Disclaimer

This is research software and an experimental acquisition protocol. It is provided without warranty and is not validated for safety-critical use. Operators remain responsible for safe bicycle operation, participant protection, sensor mounting, legal compliance, and independent validation of synchronization and data integrity.
