from prometheus_client import start_http_server, Summary, Gauge
import pandas as pd
import mlflow
import requests
import json
import time
import os
from datetime import datetime

PROMETHEUS_HOST=os.environ["PROMETHEUS_HOST"]
LOGGED_MODEL=os.environ["LOGGED_MODEL"]
NETWORK_ANOMALY = Gauge('node_network_anomaly', 'Anomaly Score of Network Data')

def get_network_data(metric, rate_base, suffix):
    prom_query = f'http://{PROMETHEUS_HOST}:9090/api/v1/query?query=rate({metric}[{rate_base}])'
    resp = requests.get(prom_query)
    input_data = json.loads(resp.text)
    df = pd.DataFrame({x['metric']['device']: [float(x['value'][1])] for x in input_data['data']['result']})
    for column in df.columns:
        df.rename(columns={column: column + suffix}, inplace=True)
    df = df[['br-0c6e79cd156e' + suffix, 'br-8fbdbc8e9f6a' + suffix, 'docker0' + suffix, 'eth0' + suffix, 'lo' + suffix]]
    return df


if __name__ == '__main__':
    start_http_server(8000)

    remote_server_uri = "http://mlflow:5000"  # set to your server URI, e.g. http://127.0.0.1:8080
    mlflow.set_tracking_uri(remote_server_uri)

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(LOGGED_MODEL)
    while True:
        node_network_receive_bytes_total = get_network_data('node_network_receive_bytes_total', '1m',  ' - Rx in')
        node_network_transmit_bytes_total = get_network_data('node_network_transmit_bytes_total', '1m',  ' - Tx in')
        node_network_receive_packets_total = get_network_data('node_network_receive_packets_total', '1m',  ' - Pck in')
        node_network_transmit_packets_total = get_network_data('node_network_transmit_packets_total', '1m',  ' - Pck out')

        network_df = pd.concat([node_network_receive_bytes_total, node_network_transmit_bytes_total], axis=1)
        network_df = pd.concat([network_df, node_network_receive_packets_total], axis=1)
        network_df = pd.concat([network_df, node_network_transmit_packets_total], axis=1)
        network_df = network_df[network_df.columns.sort_values()]
        NETWORK_ANOMALY.set(loaded_model.predict(network_df))
        time.sleep(30)
