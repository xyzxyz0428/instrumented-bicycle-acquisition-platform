#!/usr/bin/env python3
import os
import csv
import time
import math
from typing import List

import smbus

# -------- config --------
I2C_BUS = 1
I2C_ADDR = 0x24
REG = 0x17

SAMPLE_PERIOD_S = 0.1
FLUSH_ROWS = 500

# ---- replace with your fitted parameters ----
FIT_A = 1.0
FIT_B = 1.0
FIT_X0 = 0.0

out_dir = os.path.expanduser("~/bikelab_interface_logs")
ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
OUT_CSV = os.path.join(out_dir, f"fsr_force_{ts}.csv")


def now_unix_ns() -> int:
    return time.time_ns()


def adc_to_force_g(adc: int) -> float:
    z = max(float(adc) - FIT_X0, 0.0)
    return FIT_A * (z ** FIT_B)


def g_to_newton(force_g: float) -> float:
    return force_g * 0.00980665


class FSRForceLogger:
    def __init__(self, out_csv: str, flush_rows: int = 500):
        self.out_csv = out_csv
        self.flush_rows = int(flush_rows)

        os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

        self.bus = smbus.SMBus(I2C_BUS)
        self.rows: List[list] = []

        self._open_csv()

    def _open_csv(self):
        new_file = not os.path.exists(self.out_csv) or os.path.getsize(self.out_csv) == 0
        self.f = open(self.out_csv, "a", newline="")
        self.w = csv.writer(self.f)
        if new_file:
            self.w.writerow([
                "t_unix_ns",
                "ok",
                "adc_raw",
                "force_g",
                "force_n",
                "error",
            ])
            self.f.flush()

    def read_adc(self) -> int:
        self.bus.write_byte(I2C_ADDR, REG)
        return int(self.bus.read_word_data(I2C_ADDR, REG))

    def log_once(self):
        t = now_unix_ns()
        try:
            adc = self.read_adc()
            force_g = adc_to_force_g(adc)
            force_n = g_to_newton(force_g)
            print(adc)
            print(force_g)
            row = [t, 1, adc, force_g, force_n, ""]
        except Exception as e:
            row = [t, 0, math.nan, math.nan, math.nan, str(e)]

        self.rows.append(row)

        if len(self.rows) >= self.flush_rows:
            self.flush()

    def flush(self):
        if not self.rows:
            return
        self.w.writerows(self.rows)
        self.f.flush()
        self.rows.clear()

    def close(self):
        try:
            self.flush()
        finally:
            try:
                self.f.close()
            except Exception:
                pass
            try:
                self.bus.close()
            except Exception:
                pass

    def run(self, period_s: float = 0.1):
        print(f"[INFO] Logging FSR force to {self.out_csv}")
        next_t = time.time()
        try:
            while True:
                self.log_once()

                next_t += period_s
                sleep_s = next_t - time.time()
                if sleep_s > 0:
                    time.sleep(sleep_s)
                else:
                    next_t = time.time()
        except KeyboardInterrupt:
            print("\n[INFO] Ctrl-C received. Flushing and exiting…")
        finally:
            self.close()
            print("[INFO] Done.")


if __name__ == "__main__":
    logger = FSRForceLogger(out_csv=OUT_CSV, flush_rows=FLUSH_ROWS)
    logger.run(period_s=SAMPLE_PERIOD_S)
