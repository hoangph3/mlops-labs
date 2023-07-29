SHELL := /bin/bash
PACKAGE_NAME = hoangph3/spark-cluster

DOCKER_IMG := $(PACKAGE_NAME):3.2.0

build:
	docker build -t $(DOCKER_IMG) .

start:
	docker-compose up -d

job:
	/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	--jars /opt/spark/examples/postgresql-42.5.1.jar \
	--driver-memory 1G \
	--executor-memory 1G \
	/opt/spark/examples/main.py
