#!/usr/bin/env python3
import csv
import math
import sys
import numpy as np
from scipy.optimize import curve_fit


def model_power(x, a, b):
    return a * np.power(x, b)


def model_power_offset(x, a, b, x0):
    z = np.maximum(x - x0, 1e-9)
    return a * np.power(z, b)


def read_points(csv_path):
    force_g = []
    adc_mean = []

    with open(csv_path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            force = float(row["force_g"])
            adc = float(row["adc_mean"])
            if force > 0 and adc > 0:
                force_g.append(force)
                adc_mean.append(adc)

    return np.array(adc_mean), np.array(force_g)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fit_fsr_calibration.py calibration_points.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    x, y = read_points(csv_path)

    # Model 1: F = a * ADC^b
    p1, _ = curve_fit(model_power, x, y, p0=[1e-3, 2.0], maxfev=10000)
    y1 = model_power(x, *p1)
    rmse1 = np.sqrt(np.mean((y - y1) ** 2))

    # Model 2: F = a * (ADC - x0)^b
    x0_guess = max(0.0, np.min(x) * 0.8)
    bounds = ([0, 0, -1e9], [1e9, 10, np.max(x) - 1e-6])
    p2, _ = curve_fit(model_power_offset, x, y, p0=[1e-3, 2.0, x0_guess], bounds=bounds, maxfev=20000)
    y2 = model_power_offset(x, *p2)
    rmse2 = np.sqrt(np.mean((y - y2) ** 2))

    print("\n=== Fit results ===")
    print(f"Model 1: F_g = a * ADC^b")
    print(f"  a = {p1[0]:.12g}")
    print(f"  b = {p1[1]:.12g}")
    print(f"  RMSE = {rmse1:.6f} g")

    print(f"\nModel 2: F_g = a * (ADC - x0)^b")
    print(f"  a  = {p2[0]:.12g}")
    print(f"  b  = {p2[1]:.12g}")
    print(f"  x0 = {p2[2]:.12g}")
    print(f"  RMSE = {rmse2:.6f} g")

    if rmse2 <= rmse1:
        print("\n[INFO] Recommended model: Model 2")
    else:
        print("\n[INFO] Recommended model: Model 1")


if __name__ == "__main__":
    main()
