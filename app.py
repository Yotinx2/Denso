from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point, WriteApi , WritePrecision
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) 

influxdb_url = "http://localhost:8086"  
bucket = "cbm"
org = "cbm"
token = "o8zaAgQtH20dtxRHujzTMZOXm2jUoNIAQs2ZzUke_wr4bUxcGKR-igFCxr-3sCd5u2pWzm8RjfLrx48nCXGZMw=="

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
    
    query_upper_abnormal = f'''
    from(bucket: "{bucket}")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "upper_abnormal")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''

    query_lower_abnormal = f'''
    from(bucket: "{bucket}")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "lower_abnormal")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''

    query_upper_warning = f'''
    from(bucket: "{bucket}")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "upper_warning")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''

    query_lower_warning = f'''
    from(bucket: "{bucket}")
        |> range(start: -10y)
        |> filter(fn: (r) => r["_measurement"] == "thresholds")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")
        |> filter(fn: (r) => r["threshold_type"] == "lower_warning")
        |> filter(fn: (r) => r["zone"] == "{zone}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
    '''
    
    query_api = client.query_api()
    
    tables_upper_abnormal = query_api.query(query=query_upper_abnormal, org=org)
    tables_lower_abnormal = query_api.query(query=query_lower_abnormal, org=org)
    tables_upper_warning = query_api.query(query=query_upper_warning, org=org)
    tables_lower_warning = query_api.query(query=query_lower_warning, org=org)

    thresholds = {}
    for table in tables_upper_abnormal:
        for record in table.records:
            thresholds['upper_abnormal'] = record["_value"]

    for table in tables_lower_abnormal:
        for record in table.records:
            thresholds['lower_abnormal'] = record["_value"]

    for table in tables_upper_warning:
        for record in table.records:
            thresholds['upper_warning'] = record["_value"]

    for table in tables_lower_warning:
        for record in table.records:
            thresholds['lower_warning'] = record["_value"]

    return jsonify(thresholds)

@app.route('/update-thresholds', methods=['POST'])
def update_thresholds():
    data = request.json

    zone = data.get('zone', '')
    machine_id = data.get('machine_id', '')
    sensor_type = data.get('sensor_type', '')
    upper_abnormal_value = data.get('upper_abnormal', None)
    lower_abnormal_value = data.get('lower_abnormal', None)
    upper_warning_value = data.get('upper_warning', None)
    lower_warning_value = data.get('lower_warning', None)

    if upper_abnormal_value is not None:
        point_apnormal = Point("thresholds") \
            .tag("zone", zone) \
            .tag("machine_id", machine_id) \
            .tag("sensor_type", sensor_type) \
            .tag("threshold_type", "upper_abnormal") \
            .field("value", float(upper_abnormal_value)) \
            .time(datetime.utcnow(), WritePrecision.NS)

        try:
            write_api = client.write_api()
            write_api.write(bucket= bucket, org=org, record=point_apnormal)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            return jsonify({"error": str(e)}), 500

    if lower_abnormal_value is not None:
        point_apnormal = Point("thresholds") \
            .tag("zone", zone) \
            .tag("machine_id", machine_id) \
            .tag("sensor_type", sensor_type) \
            .tag("threshold_type", "lower_abnormal") \
            .field("value", float(lower_abnormal_value)) \
            .time(datetime.utcnow(), WritePrecision.NS)

        try:
            write_api = client.write_api()
            write_api.write(bucket= bucket, org=org, record=point_apnormal)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            return jsonify({"error": str(e)}), 500

    if upper_warning_value is not None:
        point_warning = Point("thresholds") \
            .tag("zone", zone) \
            .tag("machine_id", machine_id) \
            .tag("sensor_type", sensor_type) \
            .tag("threshold_type", "upper_warning") \
            .field("value", float(upper_warning_value)) \
            .time(datetime.utcnow(), WritePrecision.NS)

        try:
            write_api = client.write_api()
            write_api.write(bucket= bucket, org=org, record=point_warning)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            return jsonify({"error": str(e)}), 500

    if lower_warning_value is not None:
        point_warning = Point("thresholds") \
            .tag("zone", zone) \
            .tag("machine_id", machine_id) \
            .tag("sensor_type", sensor_type) \
            .tag("threshold_type", "lower_warning") \
            .field("value", float(lower_warning_value)) \
            .time(datetime.utcnow(), WritePrecision.NS)

        try:
            write_api = client.write_api()
            write_api.write(bucket= bucket, org=org, record=point_warning)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Thresholds updated successfully"})


@app.route('/api/static-data', methods=['GET'])
def get_data():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    zone = request.args.get('zone', default="zone_1", type=str)
    machine_id = request.args.get('machine_id', default="machine_1", type=str)
    sensor_type = request.args.get('sensor_type', default="current", type=str)
    

    print(f"Zone: {zone}, Machine ID: {machine_id}, Sensor Type: {sensor_type}, Start Time: {start_time}, End Time: {end_time}")  # Debugging

    query = f'''
    from(bucket: "{bucket}")
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
