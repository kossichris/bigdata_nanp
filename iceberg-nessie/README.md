# 🦞 bigdata_nanp - ICEBERG + NESSIE — BigData lakehouse catalog stack

Lakehouse catalog stack with **Apache Iceberg**, **Project Nessie** version-control catalog, **Trino** distributed SQL engine, and **MinIO** object storage.

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a *BigData lakehouse catalog stack* running over *Docker*.

It provides an Iceberg REST catalog backed by Nessie (with Git-like branching and time travel), queryable via Trino and with data stored in MinIO.

## **Components**

| Container | Image | Role |
|---|---|---|
| `catalog` | `ghcr.io/projectnessie/nessie:0.99.0` | Nessie Iceberg REST catalog |
| `mariadb` | `mariadb:10.11` | Nessie metadata storage |
| `trino` | `trinodb/trino:479` | Trino coordinator (SQL query engine) |
| `trino-worker` | `trinodb/trino:479` | Trino worker node |
| `minio` | `quay.io/minio/minio:latest` | S3-compatible data lake storage |

## **Ports**

| Service | Default port | Exposed port |
|---|---|---|
| Nessie REST catalog | 19120 | **19720** |
| MariaDB | 3306 | **3316** |
| Trino coordinator | 8080 | **18080** |
| Trino worker | 8081 | (internal) |
| MinIO S3 API | 9000 | **9030** |
| MinIO Web UI | 9001 | **9031** |

---

## **Run the stack**

```bash
# Navigate to this folder
cd iceberg-nessie

# Start all services
docker compose up -d

# Stop all and clean volumes
docker compose down -v --remove-orphans
```

---

## **Access UIs**

| UI | URL |
|---|---|
| Trino Web UI | http://localhost:18080 |
| Nessie REST API | http://localhost:19720/api/v2/config |
| MinIO Web Console | http://localhost:9031 (admin / password123) |

---

## **Query Iceberg tables with Trino**

Connect to Trino via CLI:

```bash
docker exec -it trino trino
```

Example SQL queries:

```sql
-- List catalogs
SHOW CATALOGS;

-- Use the Iceberg catalog (configured to point to Nessie)
USE iceberg.db;

-- Create an Iceberg table
CREATE TABLE iceberg.db.clients (
    id BIGINT,
    name VARCHAR,
    created_at TIMESTAMP
) WITH (format = 'PARQUET');

-- Insert data
INSERT INTO iceberg.db.clients VALUES (1, 'Acme Corp', CURRENT_TIMESTAMP);

-- Query data
SELECT * FROM iceberg.db.clients;

-- Time travel (snapshot-based)
SELECT * FROM iceberg.db.clients FOR VERSION AS OF <snapshot_id>;
```

---

## **Nessie catalog — branching & time travel**

```bash
# Nessie REST API — list branches
curl http://localhost:19720/api/v2/trees

# Create a branch
curl -X POST "http://localhost:19720/api/v2/trees" \
  -H "Content-Type: application/json" \
  -d '{"type":"BRANCH","name":"dev","reference":{"type":"BRANCH","name":"main"}}'
```
