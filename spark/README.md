# 🦞 bigdata_nanp - SPARK — BigData batch processing stack

Batch processing stack with **Apache Spark**, **Jupyter PySpark**, and **MinIO** (S3-compatible storage).

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a *BigData batch processing stack* running over *Docker*.

It provides a standalone Spark cluster with Jupyter notebooks for interactive PySpark development and batch jobs reading/writing data from MinIO.

## **Components**

| Container | Image | Role |
|---|---|---|
| `spark-master` | `apache/spark-py:v3.4.0` | Spark master node |
| `spark-worker-1` | `apache/spark-py:v3.4.0` | Spark worker node |
| `jupyter-pyspark` | `jupyter/pyspark-notebook:spark-3.4.0` | Jupyter notebook (PySpark kernel) |
| `minio` | `quay.io/minio/minio:latest` | S3-compatible object storage |

## **Ports**

| Service | Default port | Exposed port |
|---|---|---|
| Spark Master Web UI | 8080 | **8980** |
| Spark Master RPC | 7077 | **7977** |
| Spark Worker-1 Web UI | 8081 | **8981** |
| Jupyter | 8888 | **8988** |
| MinIO S3 API | 9000 | **9030** |
| MinIO Web UI | 9001 | **9031** |

---

## **Volumes**

Before starting the stack, update the volume device paths in `compose.yml`:

```yml
volumes:
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
cd spark

# Start all services
docker compose up -d

# Stop all and clean volumes
docker compose down -v --remove-orphans
```

---

## **Access UIs**

| UI | URL |
|---|---|
| Spark Master | http://localhost:8980 |
| Spark Worker | http://localhost:8981 |
| Jupyter Notebook | http://localhost:8988 |
| MinIO Web Console | http://localhost:9031 (admin / password123) |

---

## **PySpark with MinIO (S3)**

The Jupyter container includes the necessary Spark packages (`iceberg-runtime`, `hadoop-aws`, `aws-java-sdk`) to read and write data on MinIO using the S3A protocol.

Example Spark session in a notebook:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MinIO Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# Read parquet from MinIO
df = spark.read.parquet("s3a://my-bucket/data.parquet")
df.show()
```

---

## **MinIO operations**

```bash
# Access MinIO console at http://localhost:9031 (admin / password123)

# Delete a bucket
docker exec minio mc rb --force myalias/[bucket-name]
```
