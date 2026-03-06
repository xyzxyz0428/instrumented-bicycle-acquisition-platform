#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from bikelab_interfaces.msg import BikeSpeedData, PowerMeterData  # Import custom messages
from openant.easy.node import Node as ANTNode
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.bike_speed_cadence import BikeSpeed, BikeSpeedData as ANT_BikeSpeedData
from openant.devices.power_meter import PowerMeter, PowerData
import math

WHEEL_CIRCUMFERENCE_M = 2.20114
def nan():
    return float("nan")
        

class BikeSensorNode(Node):
    def __init__(self, bike_speed_id=18412, power_meter_id=64434):
        super().__init__('bike_sensor_node')

        # Set up ROS publishers
        self.speed_publisher = self.create_publisher(BikeSpeedData, 'bike_speed_data', 10)
        self.power_publisher = self.create_publisher(PowerMeterData, 'power_meter_data', 10)

        # Initialize ANT+ node and devices
        self.ant_node = ANTNode()
        self.ant_node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        self.bike_speed_device = BikeSpeed(self.ant_node, device_id=bike_speed_id)
        self.power_meter_device = PowerMeter(self.ant_node, device_id=power_meter_id)

        # Assign callbacks for ANT+ devices
        self.bike_speed_device.on_found = self.on_bike_speed_found
        self.bike_speed_device.on_device_data = self.on_bike_speed_data
        self.power_meter_device.on_found = self.on_power_meter_found
        self.power_meter_device.on_device_data = self.on_power_meter_data

        from collections import Counter
        self.page_counter = Counter()
        self.last_stat_t = self.get_clock().now().nanoseconds

        import os
        self.page_log_path = os.path.expanduser("~/bikelab_interface_logs/power_pages.txt")
        os.makedirs(os.path.dirname(self.page_log_path), exist_ok=True)
        self.page_set = set()

        # Start ANT+ node
        self.get_logger().info("Starting ANT+ devices, press Ctrl-C to finish")
        self.ant_node.start()

    def on_bike_speed_found(self):
        self.get_logger().info(f"Bike Speed Device {self.bike_speed_device} found and receiving")

    def on_power_meter_found(self):
        self.get_logger().info(f"Power Meter Device {self.power_meter_device} found and receiving")

    def on_bike_speed_data(self, page: int, page_name: str, data):
        if isinstance(data, ANT_BikeSpeedData):
            speed = data.calculate_speed(WHEEL_CIRCUMFERENCE_M)
            distance = data.calculate_distance(WHEEL_CIRCUMFERENCE_M)

            # Only publish if speed is not None
            if speed is not None:
                speed_msg = BikeSpeedData()
                speed_msg.speed = speed
                speed_msg.distance = distance 
                speed_msg.header = Header()
                speed_msg.header.stamp = self.get_clock().now().to_msg()  # Set the timestamp

                # Log and publish message
                #self.get_logger().info("Publishing bike speed data")
                self.speed_publisher.publish(speed_msg)

    def on_power_meter_data(self, page: int, page_name: str, data):
        # --- page discovery (keep this at the top) ---
        self.page_counter[page] += 1
        self.page_set.add(page)
        now = self.get_clock().now().nanoseconds
        if now - self.last_stat_t > 10_000_000_000:  # 10s
            s = ", ".join([f"0x{k:02X}:{v}" for k, v in self.page_counter.most_common()])
            #self.get_logger().info(f"PowerMeter pages (last 10s): {s}")
            with open(self.page_log_path, "w") as f:
                f.write("\n".join([f"0x{p:02X}" for p in sorted(self.page_set)]))
            self.page_counter.clear()
            self.last_stat_t = now

        if not isinstance(data, PowerData):
            return

        # ---- only publish on 0x10 and 0x12 ----
        if page not in (0x10, 0x12):
            return

        msg = PowerMeterData()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()

        # Default everything to NaN (means "missing / not on this page")
        msg.angular_velocity = nan()
        msg.average_power = nan()
        msg.cadence = nan()
        msg.instantaneous_power = nan()
        msg.left_power = nan()
        msg.right_power = nan()
        msg.torque = nan()

        # cadence is present on both 0x10 and 0x12 in common practice,
        # but 255 is often used as "invalid/unknown"
        if int(data.cadence) != 255:
            msg.cadence = float(data.cadence)

        if page == 0x10:
            # raw decoded instantaneous power exists on 0x10
            # 0 is VALID and must stay 0
            msg.instantaneous_power = float(data.instantaneous_power)

            # left/right: XC100 usually unavailable (often -1). Only publish if >=0.
            if int(data.left_power) >= 0:
                msg.left_power = float(data.left_power)
            if int(data.right_power) >= 0:
                msg.right_power = float(data.right_power)

            # DO NOT publish avg/torque/omega (derived) -> keep NaN

        elif page == 0x12:
            # You requested no calculated data.
            # So on 0x12 we publish ONLY cadence (already handled above),
            # and keep instantaneous_power/avg/torque/omega as NaN.
            pass

        self.power_publisher.publish(msg)

    def destroy_node(self):
        self.bike_speed_device.close_channel()
        self.power_meter_device.close_channel()
        self.ant_node.stop()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    bike_sensor_node = BikeSensorNode()

    try:
        rclpy.spin(bike_sensor_node)
    except KeyboardInterrupt:
        bike_sensor_node.get_logger().info("Shutting down bike_sensor_node.")
    finally:
        bike_sensor_node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
