from prometheus_client import start_http_server, Summary, Gauge
import pandas as pd
import mlflow
import requests
import json
import time
import os

PROMETHEUS_HOST=os.environ["PROMETHEUS_HOST"]
AWS_ACCESS_KEY_ID=os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY=os.environ["AWS_SECRET_ACCESS_KEY"]
MLFLOW_S3_ENDPOINT_URL=os.environ["MLFLOW_S3_ENDPOINT_URL"]
LOGGED_MODEL=os.environ["LOGGED_MODEL"]
NETWORK_ANOMALY = Gauge('node_network_receive_bytes_total_anomaly', 'Anomaly Score of Network Rx')
PROM_QUERY = f"http://{PROMETHEUS_HOST}:9090/api/v1/query?query=node_network_receive_bytes_total"

def get_network_data():
    resp = requests.get(PROM_QUERY)
    input_data = json.loads(resp.text)
    df = pd.DataFrame({x['metric']['device']: [float(x['value'][1])] for x in input_data['data']['result']})
    df = df[['br-0c6e79cd156e', 'br-8fbdbc8e9f6a', 'docker0', 'eth0', 'lo']]
    return df


if __name__ == '__main__':
    start_http_server(8000)

    remote_server_uri = "http://mlflow:5000"  # set to your server URI, e.g. http://127.0.0.1:8080
    mlflow.set_tracking_uri(remote_server_uri)

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(LOGGED_MODEL)
    while True:
        input_data = get_network_data()
        NETWORK_ANOMALY.set(loaded_model.predict(input_data))
        time.sleep(30)
