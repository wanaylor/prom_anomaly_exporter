# prom_anomaly_exporter
Anomaly detection exporter for Prometheus

# Example Case
This example is for anomaly detection in network traffic. The network traffic was taken from a Linux node exporter that was being queried by Prometheus. An Isolation Forest model was trained on that data and registered to MLFlow. The anomaly exporter will read the same metrics from the Prometheus node, run inference using MLFlow, and publish the anomaly to a new metric on the Prometheus node. The network anomaly can then be pulled into Grafana and visualized side by side with the network traffic.

![anomaly-exporter drawio](https://github.com/user-attachments/assets/4a240b6b-b77a-4d8f-af4f-14d919b735af)

<img width="818" alt="network_anomaly" src="https://github.com/user-attachments/assets/36e7cde0-e351-46a0-90d5-373e57542d62" />

The model was trained on Rx and Tx bytes and packets for various interfaces on the machine (20 columns total). Negative isolation forest scores indicate anomalies and the plot below shows the anomaly score along side network traffic for the selected interfaces.

![network_anomaly](https://github.com/user-attachments/assets/6b65ab91-8697-4ba3-a769-e7f4fa79475d)


# Minio Setup
There is a step in minio setup that requires creating a new bucket. Rather than leaving the script in the compose file I only ran it once and then removed it. See [here](https://mlflow.org/docs/latest/tracking/tutorials/remote-server/#create-composeyaml) for details.

# Building Containers
The official MLFlow container image does not include the required binaries for Postgres so we have to build our own. The anomaly exporter will also need to be built.

`docker build -t mlflow:2.22.1 -f Dockerfiler-mlflow .`

`docker build -t anomaly-exporter -f Dockerfiler-anomaly-exporter .`

# Env files
Move the MLFlow file into /secrets and make the required edits. Edit the .env file and fill in the correct values, or also move it to /secrets and update the compose file.
