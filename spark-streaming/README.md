# 🦞 bigdata_nanp - SPARK STREAMING — BigData structured streaming stack

Structured streaming stack with **Apache Spark**, **Redpanda** (Kafka-compatible broker), **Kafka Connect**, **MySQL** CDC, and **Jupyter PySpark**.

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a *BigData structured streaming stack* running over *Docker*.

It combines Redpanda (Kafka-compatible) as the message bus with Spark Structured Streaming to process CDC events from MySQL in real time, using Jupyter for interactive development.

## **Components**

| Container | Image | Role |
|---|---|---|
| `redpanda-0` | `redpandadata/redpanda:v25.3.9` | Kafka-compatible streaming broker |
| `redpanda-console` | `redpandadata/console:v3.5.3` | Web UI for Redpanda cluster |
| `connect` | custom | Kafka Connect (Debezium MySQL source + S3 sink) |
| `mysql` | `mysql:8.0` | Source database TYROK |
| `streamlit_app` | custom | Streamlit dashboard for MySQL data |
| `setup-automation` | custom | Initialize MySQL + register connectors |
| `spark-master` | `apache/spark-py:v3.4.0` | Spark master node |
| `spark-worker-1` | `apache/spark-py:v3.4.0` | Spark worker 1 |
| `spark-worker-2` | `apache/spark-py:v3.4.0` | Spark worker 2 |
| `jupyter-pyspark` | `jupyter/pyspark-notebook:spark-3.4.0` | Jupyter notebook (Spark Streaming) |

## **Ports**

| Service | Default port | Exposed port |
|---|---|---|
| Redpanda Kafka | 9092 | **19092** |
| Redpanda Schema Registry | 8081 | **18081** |
| Redpanda Pandaproxy | 8082 | **18082** |
| Redpanda Web Console | 8080 | **8200** |
| Kafka Connect REST API | 8083 | **8093** |
| MySQL | 3306 | **8889** |
| Streamlit | 8501 | **8541** |
| Spark Master Web UI | 8080 | **8980** |
| Spark Worker-1 Web UI | 8081 | **8981** |
| Spark Worker-2 Web UI | 8082 | **8982** |
| Jupyter | 8888 | **8988** |

---

## **Run the stack**

```bash
# Navigate to this folder
cd spark-streaming

# Start all services
docker compose up -d

# Stop all and clean volumes
docker compose down -v --remove-orphans
```

---

## **Access UIs**

| UI | URL |
|---|---|
| Redpanda Console | http://localhost:8200 |
| Kafka Connect | http://localhost:8093/connectors |
| Spark Master | http://localhost:8980 |
| Jupyter Notebook | http://localhost:8988 |

---

## **Spark Structured Streaming from Redpanda/Kafka**

Example in a Jupyter notebook:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Spark Streaming from Kafka") \
    .getOrCreate()

# Read stream from Redpanda (Kafka protocol)
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda-0:9092") \
    .option("subscribe", "TYROK.client") \
    .option("startingOffsets", "earliest") \
    .load()

df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .format("console") \
    .start() \
    .awaitTermination()
```

---

## **Kafka Connect operations**

```bash
# List connectors
curl http://localhost:8093/connectors

# Register source connector manually
curl -X POST http://localhost:8093/connectors \
  -H "Content-Type: application/json" \
  -d @tyrok-source-connector.json

# Check connector status
curl http://localhost:8093/connectors/tyrok-source-connector/status
```
