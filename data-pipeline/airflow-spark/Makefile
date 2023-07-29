SHELL := /bin/bash

build_airflow:
	docker build -f airflow/$(tag)/Dockerfile -t hoangph3/airflow:2.6.3-$(tag) airflow/$(tag)

build_spark:
	docker build -f spark/Dockerfile -t hoangph3/spark:3.4.1 spark

deploy_all:
	docker-compose up -d

echo:
	@echo $(AIRFLOW_IMG):$(VERSION)-$(tag)
