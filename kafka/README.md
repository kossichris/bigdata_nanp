# 🦞 bigdata_nanp - KAFKA — BigData CDC streaming stack

CDC (Change Data Capture) streaming pipeline to ingest data from `MySQL` and store it in `Parquet` format in `MinIO` via Apache Kafka (KRaft mode) + Kafka Connect + Schema Registry.

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a *BigData CDC streaming stack* running over *Docker*.

It deploys a streaming pipeline using **Apache Kafka** (KRaft mode, no Zookeeper), **Debezium** (MySQL source connector), and **Confluent S3 Sink** (MinIO) with **Avro/Schema Registry**.

## **Components**

| Container | Image | Role |
|---|---|---|
| `kafka` | `apache/kafka:4.2.0-rc2` | Kafka broker (KRaft mode) |
| `mysql` | `mysql:8.0` | Source database TYROK |
| `schema-registry` | `confluentinc/cp-schema-registry:7.5.0` | Avro schema management |
| `connect` | `confluentinc/cp-kafka-connect-base:7.7.7` | Kafka Connect (Debezium + S3 sink) |
| `minio` | `quay.io/minio/minio:latest` | S3-compatible object storage |
| `setup-automation` | custom | Initialize MySQL + register connectors *(profile: `extra`)* |
| `python_base` | custom | Python CLI for MySQL & MinIO *(profile: `client`, `terminal`)* |
| `streamlit_app` | custom | Streamlit dashboard *(profile: `client`, `ui`)* |

## **Ports**

| Service | Default port | Exposed port |
|---|---|---|
| MySQL | 3306 | **8889** |
| Kafka broker | 9092 | **9292** |
| Schema Registry | 8081 | **8091** |
| Kafka Connect REST API | 8083 | **8093** |
| MinIO S3 API | 9000 | **9030** |
| MinIO Web UI | 9001 | **9031** |
| Streamlit dashboard | 8501 | **8581** |

---

## **Volumes**

Before starting the stack, update the volume device paths in `compose.yml` to match your local machine:

```yml
volumes:
  mysql_data:
    driver: local
    driver_opts:
      type: none
      device: /Change/Path/mysql
      o: bind
  minio_data:
    driver: local
    driver_opts:
      type: none
      device: /Change/Path/minio
      o: bind
  share_data:
    driver: local
    driver_opts:
      type: none
      device: /Change/Path/share_folder
      o: bind
```

---

## **Run the stack**

```bash
# Navigate to this folder
cd kafka

# Start core services (kafka, mysql, schema-registry, connect, minio)
docker compose up -d

# Start core services + setup-automation (registers connectors automatically)
docker compose --profile extra up -d

# Start core services + Python CLI client
docker compose --profile client up -d

# Start everything including Streamlit UI
docker compose --profile extra --profile client --profile ui up -d

# Stop all and clean volumes
docker compose down -v --remove-orphans
```

---

## **Setup automation**

The `setup-automation` container (profile `extra`) runs automatically:
1. Grants MySQL privileges and creates the `TYROK` database + tables
2. Registers the **Debezium MySQL source connector** (`tyrok-source-connector.json`)
3. Registers the **S3 sink connector** (`tyrok-sink-connector.json`) pointing to MinIO

If you don't use the profile, register connectors manually via the Connect REST API:

```bash
# Register source connector
curl -X POST http://localhost:8093/connectors \
  -H "Content-Type: application/json" \
  -d @tyrok-source-connector.json

# Register sink connector
curl -X POST http://localhost:8093/connectors \
  -H "Content-Type: application/json" \
  -d @tyrok-sink-connector.json

# List connectors
curl http://localhost:8093/connectors
```

---

## **Access UIs**

| UI | URL |
|---|---|
| MinIO Web Console | http://localhost:9031 (admin / password123) |
| Schema Registry | http://localhost:8091/subjects |
| Kafka Connect | http://localhost:8093/connectors |

---

## **Python clients**

### MySQL client

```bash
docker exec python_base python /app/python_mysql/main.py --help
docker exec python_base python /app/python_mysql/main.py test
docker exec python_base python /app/python_mysql/main.py list client
docker exec python_base python /app/python_mysql/main.py list product
docker exec python_base python /app/python_mysql/main.py list sales
```

### MinIO client

```bash
docker exec python_base python /app/python_minio/main.py --help
docker exec python_base python /app/python_minio/main.py list --bucket client-bucket
docker exec python_base python /app/python_minio/main.py read-all --bucket client-bucket --style fancy_grid
```

---

## **Kafka operations**

```bash
# Connect to kafka container
docker exec -it kafka bash

# List topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe a topic
/opt/kafka/bin/kafka-topics.sh --describe --topic TYROK.client --bootstrap-server localhost:9092

# Consume messages from a topic
/opt/kafka/bin/kafka-console-consumer.sh --topic TYROK.client --from-beginning --bootstrap-server localhost:9092
```
