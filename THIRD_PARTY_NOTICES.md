# Third-party notices

The root Apache License 2.0 applies only to original project material owned by Xinyu Zhang. It does not replace the licences of the components listed below.

## Included material requiring separate rights clearance

### IMU CRC lookup tables — rights clearance required

`bikelab_interfaces1/bikelab_interfaces/scripts/log_imu_to_csv.py` states that its `CRC8Table` and `CRC16Table` were copied from `crc_table.cpp`. The values match [`NDHANA94/ros2_wheeltec_n100_imu/src/crc_table.cpp`](https://github.com/NDHANA94/ros2_wheeltec_n100_imu/blob/master/src/crc_table.cpp). As reviewed on 22 October 2026, that upstream repository had no licence file and its `package.xml` contained `TODO: License declaration`. This is active acquisition code: `bikelab_interfaces1/start_recording.sh` launches this IMU logger, which calculates both CRC values for every accepted IMU frame and records the integrity results.

The tables are therefore not asserted to be original Xinyu Zhang material, and the root Apache-2.0 licence does not grant rights in them. Before public redistribution, obtain written permission or an explicit upstream licence from the relevant copyright holder, or exclude/replace the affected material after technical and legal review. Retaining this notice does not itself cure the missing permission.

## External dependency not distributed by this repository

### Tobii Glasses 3 Python Library

The Tobii `glasses3-pylib` source code is not included in this repository, its reachable combined history, or its release archives.

Under this project's non-redistribution model, users must obtain the dependency directly from the [official Tobii repository](https://github.com/tobii/glasses3-pylib), check out the exact commit documented in the project README, and accept the terms applicable to their own download and use. The Tobii library is not covered by this project's Apache License 2.0, and no Tobii source, binary, or locally modified copy is included in this repository or its reachable release history.

`bikelab_interfaces2/tobii_tools/save_record.py` was independently written by Xinyu Zhang. It is original project software and is licensed under Apache-2.0. Publishing this controller does not redistribute or sublicense the separately obtained Tobii library.

## Runtime dependencies

ROS 2, Python packages, system packages, device drivers, and other runtime dependencies are not redistributed unless their files are explicitly present in this repository. Each remains subject to its own upstream licence.
