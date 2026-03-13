# 🦞 bigdata_nanp - SPARK + NESSIE — BigData lakehouse stack

Lakehouse stack with **Apache Spark**, **Apache Iceberg** table format, **Project Nessie** catalog, **Jupyter PySpark**, and **MinIO**.

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a *BigData lakehouse stack* running over *Docker*.

It combines Spark with the Iceberg open table format managed by a Nessie version-control catalog, enabling ACID transactions, time travel, and schema evolution on data stored in MinIO.

## **Components**

| Container | Image | Role |
|---|---|---|
| `spark-master` | `apache/spark-py:v3.4.0` | Spark master node |
| `spark-worker-1` | `apache/spark-py:v3.4.0` | Spark worker node |
| `jupyter-pyspark` | `jupyter/pyspark-notebook:spark-3.4.0` | Jupyter notebook (PySpark + Iceberg + Nessie) |
| `minio` | `quay.io/minio/minio:latest` | S3-compatible data lake storage |
| `catalog` | `ghcr.io/projectnessie/nessie:0.99.0` | Nessie Iceberg REST catalog |
| `mariadb` | `mariadb:10.11` | Nessie catalog metadata storage |

## **Ports**

| Service | Default port | Exposed port |
|---|---|---|
| Spark Master Web UI | 8080 | **8980** |
| Spark Master RPC | 7077 | **7977** |
| Spark Worker Web UI | 8081 | **8981** |
| Jupyter | 8888 | **8988** |
| MinIO S3 API | 9000 | **9030** |
| MinIO Web UI | 9001 | **9031** |
| Nessie REST catalog | 19120 | **19720** |
| MariaDB | 3306 | **3416** |

---

## **Volumes**

Before starting the stack, update volume device paths in `compose.yml`:

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
cd spark-nessie

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
| Nessie REST API | http://localhost:19720/api/v2/config |

---

## **PySpark with Iceberg + Nessie**

The Jupyter container includes Spark packages for `iceberg-runtime`, `nessie-spark-extensions`, and `hadoop-aws`.

Example Spark session in a notebook:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Iceberg + Nessie") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions") \
    .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog") \
    .config("spark.sql.catalog.nessie.uri", "http://catalog:19120/api/v1") \
    .config("spark.sql.catalog.nessie.ref", "main") \
    .config("spark.sql.catalog.nessie.warehouse", "s3a://warehouse") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# Create an Iceberg table managed by Nessie
spark.sql("CREATE TABLE nessie.db.clients (id INT, name STRING) USING iceberg")

# Time travel
spark.sql("SELECT * FROM nessie.db.clients VERSION AS OF 'main'")
```
