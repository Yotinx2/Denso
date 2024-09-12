import numpy as np
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from collections import defaultdict
# Configuration
bucket = "cbm"
org = "cbm"
token = "Er_McfbV4ihp3pq-J9Un6bnVFPG8mT5yDz2kgAiawo-UfdQxoEGkgt-ofWkBVVzP_JxLvAp74af2p0UXJ3O1jw=="
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
                upperAbnormal = 0.8 * max_value[1]
                lowerAbnormal = 0.2 * max_value[1]
                upperWarning = 0.75 * max_value[1]
                lowerWarning = 0.25 * max_value[1]

                # Insert upper abnormal threshold
                point_upperAbnormal = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "upper_abnormal") \
                    .field("value", upperAbnormal) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_upperAbnormal)

                # Insert lower abnormal threshold
                point_lowerAbnormal = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "lower_abnormal") \
                    .field("value", lowerAbnormal) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_lowerAbnormal)

                # Insert upper warning threshold
                point_upperWarning = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "upper_warning") \
                    .field("value", upperWarning) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_upperWarning)

                # Insert lower warning threshold
                point_lowerWarning = Point("thresholds") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor_type) \
                    .tag("zone", zone) \
                    .tag("threshold_type", "lower_warning") \
                    .field("value", lowerWarning) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point_lowerWarning)

                print(f"Inserted thresholds for {machine_id} - {sensor_type} in {zone}")
insert_initial_thresholds()

# Query for upper abnormal threshold
query_upperAbnormal = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "upper_abnormal")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''

# Similarly, for lower abnormal, upper warning, and lower warning
query_lowerAbnormal = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "lower_abnormal")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''

query_upperWarning = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "upper_warning")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''

query_lowerWarning = '''
from(bucket: "Dummy_CBM")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "thresholds")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["machine_id"] == "machine_1")
  |> filter(fn: (r) => r["sensor_type"] == "current")
  |> filter(fn: (r) => r["threshold_type"] == "lower_warning")
  |> filter(fn: (r) => r["zone"] == "zone_1")
  |> sort(columns: ["_time"], desc: true)
'''

# Execute the queries
query_api = client.query_api()
tables_upperAbnormal = query_api.query(query=query_upperAbnormal, org=org)
tables_lowerAbnormal = query_api.query(query=query_lowerAbnormal, org=org)
tables_upperWarning = query_api.query(query=query_upperWarning, org=org)
tables_lowerWarning = query_api.query(query=query_lowerWarning, org=org)

# Store values
threshold_values = {}

for table in tables_upperAbnormal:
    for record in table.records:
        threshold_values[record["_time"]] = {"upper_abnormal": record["_value"]}

for table in tables_lowerAbnormal:
    for record in table.records:
        threshold_values[record["_time"]]["lower_abnormal"] = record["_value"]

for table in tables_upperWarning:
    for record in table.records:
        threshold_values[record["_time"]]["upper_warning"] = record["_value"]

for table in tables_lowerWarning:
    for record in table.records:
        threshold_values[record["_time"]]["lower_warning"] = record["_value"]

# Display threshold combinations
for time, values in threshold_values.items():
    print(f"Time: {time}, Upper Abnormal: {values.get('upper_abnormal')}, Lower Abnormal: {values.get('lower_abnormal')}, Upper Warning: {values.get('upper_warning')}, Lower Warning: {values.get('lower_warning')}")
