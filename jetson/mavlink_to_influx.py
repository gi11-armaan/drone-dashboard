from pymavlink import mavutil
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import *
import time

# MAVLink connection
mav = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)

# Wait for heartbeat
print("Waiting for MAVLink heartbeat...")
mav.wait_heartbeat()
print("Heartbeat received.")

# InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def log_point(name, fields):
    point = Point(name).tag("drone", JETSON_NAME)
    for k, v in fields.items():
        point.field(k, v)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

while True:
    msg = mav.recv_match(blocking=True)
    if not msg:
        continue

    if msg.get_type() == 'VFR_HUD':
        log_point("telemetry", {
            "airspeed": msg.airspeed,
            "groundspeed": msg.groundspeed,
            "altitude": msg.alt,
            "climb": msg.climb
        })
    elif msg.get_type() == 'SYS_STATUS':
        log_point("telemetry", {
            "battery_voltage": msg.voltage_battery / 1000.0,
            "battery_remaining": msg.battery_remaining
        })
    elif msg.get_type() == 'GLOBAL_POSITION_INT':
        log_point("position", {
            "lat": msg.lat / 1e7,
            "lon": msg.lon / 1e7,
            "alt": msg.alt / 1000.0,
            "heading": msg.hdg / 100.0 if msg.hdg != 65535 else -1
        })

    time.sleep(0.2)
