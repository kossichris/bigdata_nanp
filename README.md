# 🦞 bigdata_nanp — BigData stack (Batchs and stream over docker)
bigdata tps and stuffs

**Folders:**
- **[mysql](mysql)**: Contains sql scripts to setup mysql database
- **[nifi](nifi)**: Docker lab — batch ingestion from MySQL to MinIO via Apache NiFi
- **[kafka](kafka)**: Docker lab — CDC streaming from MySQL to MinIO via Apache Kafka (KRaft) + Kafka Connect + Schema Registry
- **[redpanda_stream](redpanda_stream)**: Docker lab — CDC streaming from MySQL to MinIO via Redpanda (Kafka-compatible) + Spark cluster
- **[spark](spark)**: Docker lab — batch processing with Apache Spark + Jupyter + MinIO
- **[spark-nessie](spark-nessie)**: Docker lab — Spark + Apache Iceberg table format managed by Nessie catalog + MinIO
- **[spark-streaming](spark-streaming)**: Docker lab — Spark Structured Streaming over Redpanda (Kafka) + Jupyter
- **[iceberg-nessie](iceberg-nessie)**: Docker lab — Apache Iceberg + Nessie catalog + Trino SQL engine + MinIO

## Versions

* SE: **Ubuntu 22.04.5 LTS**
* Runtime enviromment for test: **Docker version 29.1.5**.
* Browser: **Opera 126.x**
* Others versions: in **compose.yml**

## Install

### [Docker] (if not already installed)

- **[Install](https://docs.docker.com/engine/install/)**



```bash
# prerequises
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release -y

# Add GPG keys
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

# Update repository & install docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- **<u>Docker service</u>** 
```bash
# start & stop & status
sudo systemctl status docker
sudo systemctl start docker
sudo systemctl stop docker
```

- **<u>User access Config</u>**
```bash
# configure user
sudo groupadd docker # add group if not exist
sudo usermod -aG docker $USER
newgrp docker # Or restart session
```
---

### Docker - Start containers (per stack)

Each stack lives in its own sub-folder. Navigate to the folder you want and run `docker compose up -d`.

| Stack | Folder | Key UIs |
|---|---|---|
| NiFi batch pipeline | `nifi/` | NiFi `https://localhost:8443`, MinIO `http://localhost:9031` |
| Kafka CDC streaming | `kafka/` | Schema Registry `http://localhost:8091`, Connect `http://localhost:8093`, MinIO `http://localhost:9031` |
| Redpanda streaming + Spark | `redpanda_stream/` | Redpanda Console `http://localhost:8200`, Jupyter `http://localhost:8988`, MinIO `http://localhost:9031` |
| Spark batch + Jupyter | `spark/` | Spark Master `http://localhost:8980`, Jupyter `http://localhost:8988`, MinIO `http://localhost:9031` |
| Spark + Nessie + Iceberg | `spark-nessie/` | Spark Master `http://localhost:8980`, Jupyter `http://localhost:8988`, Nessie `http://localhost:19720` |
| Spark Structured Streaming | `spark-streaming/` | Redpanda Console `http://localhost:8200`, Jupyter `http://localhost:8988` |
| Iceberg + Nessie + Trino | `iceberg-nessie/` | Trino `http://localhost:18080`, Nessie `http://localhost:19720`, MinIO `http://localhost:9031` |

```bash
# Example: start the NiFi stack
cd nifi
docker compose up -d

# Example: start the Kafka stack (core services only)
cd kafka
docker compose up -d

# Example: start the Kafka stack including optional services (setup-automation, python clients, UI)
cd kafka
docker compose --profile extra --profile client --profile ui up -d

# Example: start the Redpanda streaming stack
cd redpanda_stream
docker compose up -d

# Example: start the Spark batch stack
cd spark
docker compose up -d

# Example: start the Spark + Nessie stack
cd spark-nessie
docker compose up -d

# Example: start the Spark Streaming stack
cd spark-streaming
docker compose up -d

# Example: start the Iceberg + Nessie + Trino stack
cd iceberg-nessie
docker compose up -d
```

### Docker - Common operations

```bash
# Be sure to be in the folder with compose.yml file

# stop all and clean some volume
docker compose down -v --remove-orphans

# logs (you can also have access to logs on portainer)
docker logs -f {container}

# Bash access of specific container
docker exec -it {container} bash

# remove unused images
docker image prune -a

# remove all container not used for the last 24h
docker container prune --filter "until=24h"

# remove unused volume
docker volume prune
```

---

### [Portainer]
```bash
# Create Docker Volume 'portainer_data'
sudo docker volume create --driver local --opt type=none --opt device={path_to_your_local_folder} --opt o=bind portainer_data

# Inspect the volume (check)
docker volume inspect portainer_data

# Start Portainer
sudo docker run -d -p 7003:8000 -p 7443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v /run/docker.sock:/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

#### Access from browser **`https://localhost:7443`**

---

### [Minio]
```bash
# delete a bucket
docker exec minio mc rb --force myalias/[nom-du-bucket]
```

#### Access from browser **`https://localhost:9031`**

---

### [Python console client]

There are two clients: **`python_mysql`** and **`python_minio`**

#### [Python Mysql client]

use to query mysql tables **`[client, product, sale]`**

**code location**: **`[base_github_folder]/[Project_folder]/python/python_mysql`**

**main py file**: **`main.py`**

**config py file**: **`config.py`** (change mysql connection config)

```bash
# Some commands

# help
docker exec python_base python /app/python/python_mysql/main.py --help

# test mysql connection
docker exec python_base python /app/python/python_mysql/main.py test

# list all clients, products and sales
docker exec python_base python /app/python/python_mysql/main.py list client
docker exec python_base python /app/python/python_mysql/main.py list product
docker exec python_base python /app/python/python_mysql/main.py list sales

# add datas
docker exec python_base python /app/python/python_mysql/main.py client --code "C003" --name "Entreprise XYZ"
docker exec python_base python /app/python/python_mysql/main.py product --code "P-TAB" --name "Tablette" --pu 299.99
docker exec python_base python /app/python/python_mysql/main.py sale --client_id 1 --product_id 2 --qte 3 --total 899.97

```


#### [Python Minio client]

use to query minio csv or parquet files

**code location**: **`[base_github_folder]/[Project_folder]/python/python_minio`**

**main py file**: **`main.py`**

**env file**: **`.env.example`** -> Rename to **`.env`** (minio configs, don't forget to change values if necessary)


```bash
# Some commands

# help
docker exec python_base python /app/python/python_minio/main.py --help

# list csv or parquet files directly under minio path
docker exec python_base python /app/python/python_minio/main.py list --bucket [my-bucket]

# list all csv or parquet files under a bucket
docker exec python_base python /app/python/python_minio/main.py list-all --bucket [my-bucket]

# count all csv or parquet files under a bucket
docker exec python_base python /app/python/python_minio/main.py count --bucket [my-bucket]

# get the content of a specific csv or parquet files under a bucket
docker exec python_base python /app/python/python_minio/main.py read --bucket [my-bucket] --file [my-file.csv | my-file.parquet] --style [grid | fancy_grid | simple]

# get the content of all csv or parquet files under a bucket
docker exec python_base python /app/python/python_minio/main.py read-all --bucket [my-bucket] --style [grid | fancy_grid | simple]

# send csv or parquet files to minio bucket
docker exec python_base python /app/python/python_minio/main.py put --bucket [my-bucket] --local [/path/to/local/file] --remote [name_in_minio]
```

---

* #### **Kafka:**

```sh
# 0- connect to kafka container
docker exec -it kafka bash
# 1- move to scripts folder
cd /opt/kafka/bin/

# list of topics created
./kafka-topics.sh --list --bootstrap-server localhost:9092
# describe a topic
./kafka-topics.sh --describe --topic [topic_name] --bootstrap-server localhost:9092
# read live data produce inside a topic
./kafka-console-consumer.sh --topic [topic_name] --from-beginning --bootstrap-server localhost:9092
```

---


