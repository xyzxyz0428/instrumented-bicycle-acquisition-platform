# Third-party notices

The root Apache License 2.0 applies only to original project material owned by Xinyu Zhang. It does not replace the licences of the components listed below.

## Included components

### RoboSense LiDAR software

The following directories contain RoboSense software:

- `rslidar_sdk/`
- `rslidar_msg/`
- `rslidar_sdk/src/rs_driver/`

Copyright © 2020 RoboSense.

These components are distributed under their included 3-clause BSD licence. Their authoritative licence texts are retained at:

- `rslidar_sdk/LICENSE`
- `rslidar_msg/LICENSE`
- `rslidar_sdk/src/rs_driver/LICENSE`

## External dependency not distributed by this repository

### Tobii Glasses 3 Python Library

The Tobii `glasses3-pylib` source code is not included in this repository, its reachable combined history, or its release archives.

Users must obtain the dependency directly from the [official Tobii repository](https://github.com/tobii/glasses3-pylib), check out the exact commit documented in the project README, and comply with the licence supplied by Tobii. It is not covered by this project's Apache License 2.0.

`tobii_tools/save_record.py` was independently written by Xinyu Zhang. It is original project software and is licensed under Apache-2.0. Its use of the public `g3pylib` interface does not place the Tobii library under the project licence.

## Runtime dependencies

ROS 2, Python packages, system packages, device drivers, and other runtime dependencies are not redistributed unless their files are explicitly present in this repository. Each remains subject to its own upstream licence.
