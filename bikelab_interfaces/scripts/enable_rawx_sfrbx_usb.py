#!/usr/bin/env python3
from serial import Serial
from pyubx2 import UBXMessage, SET_LAYER_RAM, SET_LAYER_BBR, SET_LAYER_FLASH

PORT = "/dev/ttyACM0"
BAUD = 115200
layers = SET_LAYER_RAM | SET_LAYER_BBR | SET_LAYER_FLASH

cfg = [
    ("CFG_USBOUTPROT_UBX", 1),
    ("CFG_USBINPROT_UBX", 1),
    ("CFG_USBOUTPROT_NMEA", 1),
    ("CFG_USBINPROT_RTCM3X", 1),

    ("CFG_MSGOUT_NMEA_ID_GGA_USB", 1),
    ("CFG_MSGOUT_NMEA_ID_RMC_USB", 1),

    ("CFG_MSGOUT_UBX_RXM_RAWX_USB", 1),
    ("CFG_MSGOUT_UBX_RXM_SFRBX_USB", 1),
    ("CFG_MSGOUT_UBX_NAV_PVT_USB", 1),
]

with Serial(PORT, BAUD, timeout=2) as ser:
    msg = UBXMessage.config_set(layers=layers, transaction=0, cfgData=cfg)
    ser.write(msg.serialize())
    ser.flush()

print("Restored NMEA and enabled UBX RAWX/SFRBX.")