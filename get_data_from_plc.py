import asyncio
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions
from aphyt import omron

# Configuration
bucket = "Dummy_CBM"
org = "DIMA"
token = "6MqmqE78Vs3sUI4v-lSrlYcxo57yBETHmT4cIiMBLZGzfrd-Dw2CL1IDLCnrRKxxEu9kcD6AvtyUP9mcSq7GYw=="
url = "http://localhost:8086"
PLC_ADDRESS = '192.168.250.1'

# Create InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000))

# Sensor types and their max values
threshold_cache = {}

# Function to fetch thresholds from InfluxDB and update the cache
async def fetch_thresholds():
    query = '''
    from(bucket: "Dummy_CBM")
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
sensor_tags = [
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "flow_rate_in", "tag": "FS1_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "water_temp_in", "tag": "FS1_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "flow_rate_out", "tag": "FS2_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "water_temp_out", "tag": "FS2_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "flow_rate_in", "tag": "FS3_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "water_temp_in", "tag": "FS3_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "flow_rate_out", "tag": "FS4_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "water_temp_out", "tag": "FS4_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "flow_rate_in", "tag": "FS5_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "water_temp_in", "tag": "FS5_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "flow_rate_out", "tag": "FS6_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "water_temp_out", "tag": "FS6_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "flow_rate_in", "tag": "FS7_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "water_temp_in", "tag": "FS7_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "flow_rate_out", "tag": "FS8_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "water_temp_out", "tag": "FS8_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "flow_rate_in", "tag": "FS9_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "water_temp_in", "tag": "FS9_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "flow_rate_out", "tag": "FS10_FLOW_ACT"},
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "water_temp_out", "tag": "FS10_TEMP_ACT"},
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "vibration_velocity", "tag": "VB1_VIBRATION_ACT"},
    {"zone": "zone_1", "machine_id": "machine_1", "sensor_type": "vibration_acceleration", "tag": "VB1_ACCEL_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "vibration_velocity", "tag": "VB2_VIBRATION_ACT"},
    {"zone": "zone_1", "machine_id": "machine_2", "sensor_type": "vibration_acceleration", "tag": "VB2_ACCEL_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "vibration_velocity", "tag": "VB3_VIBRATION_ACT"},
    {"zone": "zone_1", "machine_id": "machine_3", "sensor_type": "vibration_acceleration", "tag": "VB3_ACCEL_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "vibration_velocity", "tag": "VB4_VIBRATION_ACT"},
    {"zone": "zone_1", "machine_id": "machine_4", "sensor_type": "vibration_acceleration", "tag": "VB4_ACCEL_ACT"},
]

# Function to generate data for one zone, machine, and sensor
async def process_data_for_combination(zone, machine_id, sensor, tag):
    try:
        # Connect to PLC
        plc = omron.FinsClient(PLC_ADDRESS)
        value = plc.read_tag(tag)
    except Exception as e:
        print(f"Error reading from PLC: {e}")
        value = None

    if value is not None:
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
            .time(datetime.utcnow(), WritePrecision.S)

        # Create status data point
        status_point = Point("sensor_status") \
            .tag("machine_id", machine_id) \
            .tag("sensor_type", sensor) \
            .tag("zone", zone) \
            .field("value", status) \
            .time(datetime.utcnow(), WritePrecision.S)

        # Write points to InfluxDB
        write_api.write(bucket=bucket, org=org, record=[sensor_point, status_point])

# Main function to fetch thresholds and generate data
async def main():
    # Fetch thresholds from InfluxDB and update the cache
    await fetch_thresholds()

    while True:
        # Process data for all combinations of zones, machine_ids, and sensor_types
        tasks = [
            process_data_for_combination(combination['zone'], combination['machine_id'], combination['sensor_type'], combination['tag'])
            for combination in sensor_tags
        ]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)  # Run the process every 1 second

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
