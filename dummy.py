import numpy as np
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# Configuration
bucket = "test"
org = "cbm"
token = "Er_McfbV4ihp3pq-J9Un6bnVFPG8mT5yDz2kgAiawo-UfdQxoEGkgt-ofWkBVVzP_JxLvAp74af2p0UXJ3O1jw=="
url = "http://localhost:8086"

# Create InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Sensor types and their max values
sensor_types = {
    "vibration_velocity": (0, 10),
    "vibration_acceleration": (0, 100),
    "temperature": (0, 5),
    "flow_rate_in": (0, 500),
    "flow_rate_out": (0, 500),
    "water_temp_in": (0, 100),
    "water_temp_out": (0, 100),
    "current": (0, 70),
    "speed": (0, 3000)
}

machine_ids = [f"machine_{i}" for i in range(1, 6)]
zones = [f"zone_{i}" for i in range(1, 6)]

# Function to generate sensor data
def generate_sensor_data():
    for zone in zones:
        for machine_id in machine_ids:
            for sensor, (low, high) in sensor_types.items():
                value = np.random.uniform(low=low, high=high)

                # Store the sensor data
                point = Point("sensor_data") \
                    .tag("machine_id", machine_id) \
                    .tag("sensor_type", sensor) \
                    .tag("zone", zone) \
                    .field("value", value) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                write_api.write(bucket=bucket, org=org, record=point)


# Main loop for continuous data generation
try:
    while True:
        start_time = time.time()
        generate_sensor_data()
        print("Data written to InfluxDB")
        elapsed_time = time.time() - start_time
        sleep_time = max(1 - elapsed_time, 0)
        time.sleep(sleep_time)
except KeyboardInterrupt:
    print("Data generation stopped")
finally:
    client.close()
