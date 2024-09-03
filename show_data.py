from aphyt import omron

PLC_ADDRESS = '192.168.250.1'  # Replace with your actual PLC IP address

# List of sensors with their associated tags
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
    """
    Reads the data from a specified PLC tag.
    """
    try:
        sensor_value = eip_conn.read_variable(sensor_tag)
        return sensor_value
    except Exception as e:
        print(f"Error reading sensor {sensor_tag}: {e}")
        return None

def main():
    """
    Fetches and prints all sensor data once.
    """
    try:
        with omron.NSeries(PLC_ADDRESS) as eip_conn:
            print("PLC connection successful.")
            for sensor in sensor_tags:
                # Get data from each sensor
                sensor_value = get_sensor_data(eip_conn, sensor["tag"])
                
                # If data is received, print it
                if sensor_value is not None and sensor_value != "":
                    print(f"Data from Zone: {sensor['zone']}, Machine: {sensor['machine_id']}, "
                          f"Sensor Type: {sensor['sensor_type']}, Tag: {sensor['tag']} - Value: {sensor_value}")
                else:
                    print(f"No data received for Zone: {sensor['zone']}, Machine: {sensor['machine_id']}, "
                          f"Sensor Type: {sensor['sensor_type']}, Tag: {sensor['tag']}. Skipping...")

    except Exception as e:
        print(f"PLC connection failed: {e}")

if __name__ == "__main__":
    main()
