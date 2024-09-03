import numpy as np
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from collections import defaultdict
# Configuration
bucket = "Dummy_CBM"
org = "DIMA"
token = "6MqmqE78Vs3sUI4v-lSrlYcxo57yBETHmT4cIiMBLZGzfrd-Dw2CL1IDLCnrRKxxEu9kcD6AvtyUP9mcSq7GYw=="
url = "http://localhost:8086"

# # Create InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# # Sensor types and their max values
sensor_types = {
    "vibration_velocity": (0, 10.0),
    "vibration_acceleration": (0, 100.0),
    "temperature": (0, 5.0),
    "flow_rate_in": (0, 500.0),
    "flow_rate_out": (0, 500.0),
    "water_temp_in": (0, 100.0),
    "water_temp_out": (0, 100.0),
    "current": (0, 70.0),
    "speed": (0, 3000.0)
}

machine_ids = [f"machine_{i}" for i in range(1, 6)]
zones = [f"zone_{i}" for i in range(1, 6)]

def insert_initial_thresholds():
    for machine_id in machine_ids:
        for zone in zones:
            for sensor_type, max_value in sensor_types.items():
                appnormal = 0.8 * max_value[1]
                warning = 0.75 * max_value[1]

                # Insert apnormal threshold
                point_appnormal = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "apnormal") \
                    .field("value", appnormal) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_appnormal)
                # Insert warning threshold
                point_warning = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "warning") \
                    .field("value", warning) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_warning)

                print(f"Inserted thresholds for {machine_id} - {sensor_type} in {zone}")
insert_initial_thresholds()

query_appnormal = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "apnormal")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''

query_warning = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "warning")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''
query_api = client.query_api()
# Execute the queries
tables_apnormal = query_api.query(query=query_appnormal, org=org)
tables_warning = query_api.query(query=query_warning, org=org)

# Store values
apnormal_values = {}
for table in tables_apnormal:
    for record in table.records:
        apnormal_values[record["_time"]] = record["_value"]

warning_values = {}
for table in tables_warning:
    for record in table.records:
        warning_values[record["_time"]] = record["_value"]

# Combine the closest values
for time_apnormal, value_apnormal in apnormal_values.items():
    closest_time_warning = min(warning_values.keys(), key=lambda t: abs(t - time_apnormal))
    value_warning = warning_values[closest_time_warning]
    
    print(f"{value_apnormal},{value_warning}")
