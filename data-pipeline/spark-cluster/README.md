# Spark Cluster with Docker

A simple spark standalone cluster for your development environment.

Container|Exposed ports
---|---
spark-master|9090
spark-worker-1|9091
spark-worker-2|9092
my-postgres|5432

## Installation

### 1. Build the image

```sh
make build
```

### 2. Run the spark cluster

```sh
make start
```

### 3. Validate your cluster

Accessing the spark UI:

* [Spark Master](http://localhost:9090)
* [Spark Worker 1](http://localhost:9091)
* [Spark Worker 2](http://localhost:9092)

## Resource Allocation

* The default CPU cores allocation for each spark worker is 1 core.

* The default RAM for each spark worker is 1024MB.

* The default RAM allocation for spark executors is 256MB.

* The default RAM allocation for spark driver is 128MB.

* If you wish to modify this allocations just edit the env/spark-worker.sh file.

## Run sample jobs

Connect to one of the workers or the master:

```sh
docker exec -it spark-worker-1 bash
```

Then execute:

```sh
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--jars /opt/spark/examples/postgresql-42.5.1.jar \
--driver-memory 1G \
--executor-memory 1G \
/opt/spark/examples/main.py
```

Verify the database:
```
psql -h localhost -U admin -d my_db
Password for user admin: ******

my_db=# \dt
         List of relations
 Schema |   Name    | Type  | Owner 
--------+-----------+-------+-------
 public | starbucks | table | admin
(1 row)

my_db=# select * from starbucks;
         name          |  size  | price |     sale_price     
-----------------------+--------+-------+--------------------
 White Chocolate Mocha | Tall   |  3.75 |              3.375
 White Chocolate Mocha | Grande |  4.45 |              4.005
 White Chocolate Mocha | Venti  |  4.75 |              4.275
 Cinnamon Dolce Latte  | Tall   |  3.65 |              3.285
 Cinnamon Dolce Latte  | Grande |  4.25 |              3.825
 Cinnamon Dolce Latte  | Venti  |  4.65 | 4.1850000000000005
 Caramel Macchiato     | Tall   |  3.75 |              3.375
 Caramel Macchiato     | Grande |  4.45 |              4.005
 Caramel Macchiato     | Venti  |  4.75 |              4.275
(9 rows)
```
