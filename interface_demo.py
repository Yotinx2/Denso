from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

influxdb_url = "http://localhost:8086"  
token = "6MqmqE78Vs3sUI4v-lSrlYcxo57yBETHmT4cIiMBLZGzfrd-Dw2CL1IDLCnrRKxxEu9kcD6AvtyUP9mcSq7GYw=="
org = "DIMA"
bucket = "Dummy_CBM"

client = InfluxDBClient(url=influxdb_url, token=token, org=org)

from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        machine_id = request.args.get('machine_id')
        sensor_type = request.args.get('sensor_type')
        zone = request.args.get('zone')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # Add your logic to query the database and process data here
        # Example: data = query_database(machine_id, sensor_type, zone, start_time, end_time)
        
        # Dummy response for illustration
        data = [
            {"time": "2024-08-26T09:26:00.000Z", "value": 10},
            {"time": "2024-08-26T09:27:00.000Z", "value": 12}
        ]
        return jsonify(data)

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)



if __name__ == '__main__':
    app.run(debug=True)