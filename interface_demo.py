import time
from aphyt import omron
from influxdb_client import InfluxDBClient
from datetime import datetime

INFLUXDB_URL = "http://localhost:8086"  
INFLUXDB_TOKEN = "your-token"  
INFLUXDB_ORG = "your-org"  
INFLUXDB_BUCKET = "your-bucket" 

PLC_ADDRESS = '192.168.250.1' 

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api()

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
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "vibration_velocity", "tag": "VB5_VIBRATION_ACT"},
    {"zone": "zone_1", "machine_id": "machine_5", "sensor_type": "vibration_acceleration", "tag": "VB5_ACCEL_ACT"}
]

def get_sensor_data(eip_conn, sensor_tag):
    try:
        sensor_value = eip_conn.read_variable(sensor_tag)
        return sensor_value
    except Exception as e:
        print(f"Error reading sensor {sensor_tag}: {e}")
        return None

def insert_data_to_influxdb(zone, machine_id, sensor_type, value):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "measurement": "sensor_data",
        "tags": {
            "machine_id": machine_id,
            "sensor_type": sensor_type,
            "zone": zone
        },
        "fields": {
            "value": float(value)
        },
        "time": timestamp
    }
    try:
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=data)
        print(f"Data inserted: {data}")
    except Exception as e:
        print(f"Error inserting data to InfluxDB: {e}")

def main():
    while True:
        try:
            with omron.NSeries(PLC_ADDRESS) as eip_conn:
                print("PLC connection successful.")
                for sensor in sensor_tags:
                    sensor_value = get_sensor_data(eip_conn, sensor["tag"])
                    
                    if sensor_value is not None and sensor_value != "":
                        insert_data_to_influxdb(sensor["zone"], sensor["machine_id"], sensor["sensor_type"], sensor_value)
                    else:
                        print(f"Skipping insertion for {sensor['tag']} - No data received.")
        
        except Exception as e:
            print(f"PLC connection failed: {e}. Retrying...")

        time.sleep(1)

if __name__ == "__main__":
    main()
