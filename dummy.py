import asyncio
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions
import numpy as np

# Configuration
url = "http://localhost:8086"
bucket = "cbm"
org = "cbm"
token = "o8zaAgQtH20dtxRHujzTMZOXm2jUoNIAQs2ZzUke_wr4bUxcGKR-igFCxr-3sCd5u2pWzm8RjfLrx48nCXGZMw=="

# Create InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000))

# Cache for thresholds
threshold_cache = {}

# Function to fetch thresholds from InfluxDB and update the cache
async def fetch_thresholds():
    query = '''
    from(bucket: "cbm")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "thresholds")
      |> filter(fn: (r) => r["_field"] == "value")
      |> filter(fn: (r) => r["machine_id"] =~ /^machine_[1-5]$/)
      |> filter(fn: (r) => r["sensor_type"] =~ /^current$|^flow_rate_out$|^flow_rate_in$|^speed$|^temperature$|^water_temp_in$|^water_temp_out$|^vibration_acceleration$|^vibration_velocity$/)
      |> filter(fn: (r) => r["threshold_type"] =~ /^lower_abnormal$|^lower_warning$|^upper_abnormal$|^upper_warning$/)
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
      |> yield(name: "last")
    '''
    tables = client.query_api().query(query=query, org=org)

    for table in tables:
        for record in table.records:
            machine_id = record['machine_id']
            sensor_type = record['sensor_type']
            threshold_type = record['threshold_type']
            value = record['_value']

            if machine_id not in threshold_cache:
                threshold_cache[machine_id] = {}
            if sensor_type not in threshold_cache[machine_id]:
                threshold_cache[machine_id][sensor_type] = {}
            
            threshold_cache[machine_id][sensor_type][threshold_type] = value

# Function to classify status based on sensor value and thresholds
def classify_status(value, thresholds):
    upper_abnormal = thresholds.get('upper_abnormal')
    lower_abnormal = thresholds.get('lower_abnormal')
    upper_warning = thresholds.get('upper_warning')
    lower_warning = thresholds.get('lower_warning')

    if lower_abnormal is not None and value < lower_abnormal:
        return 'Abnormal'
    elif upper_abnormal is not None and value > upper_abnormal:
        return 'Abnormal'
    elif lower_warning is not None and value < lower_warning:
        return 'Warning'
    elif upper_warning is not None and value > upper_warning:
        return 'Warning'
    else:
        return 'Normal'

# Zones and sensor types configuration
zones = ["zone_1", "zone_2", "zone_3", "zone_4", "zone_5"]
machine_ids = ["machine_1", "machine_2", "machine_3", "machine_4", "machine_5"]
sensor_types = {
    "current": (0, 100),
    "flow_rate_out": (0, 100),
    "flow_rate_in": (0, 100),
    "speed": (0, 100),
    "temperature": (0, 100),
    "water_temp_in": (0, 100),
    "vibration_acceleration": (0, 100),
    "vibration_velocity": (0, 100),
}

# Function to generate data for one zone, machine, and sensor
async def process_data_for_combination(zone, machine_id, sensor, low, high):
    value = np.random.uniform(low=low, high=high)

    # Get thresholds from the cache
    thresholds = threshold_cache.get(machine_id, {}).get(sensor, {})

    # Classify the sensor data value
    status = classify_status(value, thresholds)

    # Create sensor data point
    sensor_point = Point("sensor_data") \
        .tag("machine_id", machine_id) \
        .tag("sensor_type", sensor) \
        .tag("zone", zone) \
        .field("value", value) \
        .time(datetime.utcnow(), WritePrecision.NS)

    # Create event data point
    event_point = Point("event_data") \
        .tag("machine_id", machine_id) \
        .tag("sensor_type", sensor) \
        .tag("zone", zone) \
        .tag("status", status) \
        .field("event_detail", "" )\
        .time(datetime.utcnow(), WritePrecision.NS)

    return [sensor_point, event_point]

# Function to generate sensor data for all zones, machines, and sensors
async def generate_sensor_data():
    tasks = []
    for zone in zones:
        for machine_id in machine_ids:
            for sensor, (low, high) in sensor_types.items():
                tasks.append(process_data_for_combination(zone, machine_id, sensor, low, high))

    # Gather results
    results = await asyncio.gather(*tasks)
    points = [point for sublist in results for point in sublist]

    # Write all points in a batch
    write_api.write(bucket=bucket, org=org, record=points)

# Function to refresh the threshold cache periodically
async def refresh_cache():
    while True:
        await fetch_thresholds()
        print("Threshold cache refreshed.")
        await asyncio.sleep(60)  # Refresh cache every 60 seconds

# Function to run the scheduled task
async def run_tasks():
    while True:
        await generate_sensor_data()
        print("Data generation completed.")
        await asyncio.sleep(1)  # Run data generation every second

# Main entry point
async def main():
    # Fetch thresholds once and cache them
    await fetch_thresholds()

    # Start the cache refresh and data generation tasks
    await asyncio.gather(
        refresh_cache(),
        run_tasks()
    )

# Run the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Data generation stopped")
finally:
    client.close()
