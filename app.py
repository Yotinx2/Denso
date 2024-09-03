from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point, WriteApi , WritePrecision
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) 

influxdb_url = "http://localhost:8086"  
token = "6MqmqE78Vs3sUI4v-lSrlYcxo57yBETHmT4cIiMBLZGzfrd-Dw2CL1IDLCnrRKxxEu9kcD6AvtyUP9mcSq7GYw=="
org = "DIMA"
bucket = "Dummy_CBM"

client = InfluxDBClient(url=influxdb_url, token=token, org=org)

@app.route('/api/data', methods=['GET'])
def get_staticData():
    zone = request.args.get('zone', default="zone_1", type=str)
    machine_id = request.args.get('machine_id', default="machine_1", type=str)
    sensor_type = request.args.get('sensor_type', default="current", type=str)
    
    print(f"Zone: {zone}, Machine ID: {machine_id}, Sensor Type: {sensor_type}")  # Debugging

    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -1m, stop: now())
      |> filter(fn: (r) => r["_measurement"] == "sensor_data")
      |> filter(fn: (r) => r["zone"] == "{zone}")
      |> filter(fn: (r) => r["_field"] == "value")
      |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
      |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
      |> aggregateWindow(every: 1s, fn: last, createEmpty: false)
      |> yield(name: "last")
    '''
    
    try:
        result = client.query_api().query(org=org, query=query)
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value()
                })
            
        return jsonify(data)
    except Exception as e:
        print(f"Error executing query: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/get-thresholds', methods=['GET'])
def get_thresholds():
    zone = request.args.get('zone', default="zone_1", type=str)
    machine_id = request.args.get('machine_id', default="machine_1", type=str)
    sensor_type = request.args.get('sensor_type', default="current", type=str)
    
    print(f"Zone: {zone}, Machine ID: {machine_id}, Sensor Type: {sensor_type}")  
    query_apnormal = f'''
    from(bucket: "Dummy_CBM")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "apnormal")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''

    query_warning = f'''
    from(bucket: "Dummy_CBM")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "warning")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''
    query_api = client.query_api()
    
    tables_apnormal = query_api.query(query=query_apnormal, org=org)
    tables_warning = query_api.query(query=query_warning, org=org)

    apnormal_values = {}
    for table in tables_apnormal:
        for record in table.records:
            apnormal_values[record["_time"]] = record["_value"]

    warning_values = {}
    for table in tables_warning:
        for record in table.records:
            warning_values[record["_time"]] = record["_value"]

    combined_values = []
    for time_apnormal, value_apnormal in apnormal_values.items():
        closest_time_warning = min(warning_values.keys(), key=lambda t: abs(t - time_apnormal))
        value_warning = warning_values[closest_time_warning]
        combined_values.append([value_apnormal, value_warning])


    print(combined_values)
    return jsonify(combined_values)


@app.route('/update-thresholds', methods=['POST'])
def update_thresholds():

    data = request.json

    zone = data.get('zone', '')
    machine_id = data.get('machine_id', '')
    sensor_type = data.get('sensor_type', '')
    warning_value = data.get('warning_value')
    apnormal_value = data.get('apnormal_value')

    if apnormal_value is None or warning_value is None:
        return jsonify({"error": "Both apnormal and warning values are required"}), 400

    print(f"Updating thresholds for Zone: {zone}, Machine ID: {machine_id}, Sensor Type: {sensor_type}, Apnormal Value: {apnormal_value}, Warning Value: {warning_value}")  # Debugging

    # Create points for both thresholds
    point_apnormal = Point("thresholds") \
        .tag("zone", zone) \
        .tag("machine_id", machine_id) \
        .tag("sensor_type", sensor_type) \
        .tag("threshold_type", "apnormal") \
        .field("value", float(apnormal_value)) \
        .time(datetime.utcnow(), WritePrecision.NS)

    point_warning = Point("thresholds") \
        .tag("zone", zone) \
        .tag("machine_id", machine_id) \
        .tag("sensor_type", sensor_type) \
        .tag("threshold_type", "warning") \
        .field("value", float(warning_value)) \
        .time(datetime.utcnow(), WritePrecision.NS)

    # Write both points to InfluxDB
    try:
        write_api = client.write_api()
        write_api.write(bucket="Dummy_CBM", org=org, record=[point_apnormal, point_warning])
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Both thresholds updated successfully"})


@app.route('/api/static-data', methods=['GET'])
def get_data():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    zone = request.args.get('zone', default="zone_1", type=str)
    machine_id = request.args.get('machine_id', default="machine_1", type=str)
    sensor_type = request.args.get('sensor_type', default="current", type=str)
    

    print(f"Zone: {zone}, Machine ID: {machine_id}, Sensor Type: {sensor_type}, Start Time: {start_time}, End Time: {end_time}")  # Debugging

    query = f'''
    from(bucket: "Dummy_CBM")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["zone"] == "zone_1")
        |> filter(fn: (r) => r._time >= {start_time} and r._time <= {end_time}) 
        |> yield(name: "mean")
    '''
    
    try:
        result = client.query_api().query(org=org, query=query)
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value()
                })
            
        return jsonify(data)
    except Exception as e:
        print(f"Error executing query: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
