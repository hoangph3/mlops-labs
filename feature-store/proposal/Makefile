start:
	docker-compose up -d --build

build-producer:
	docker build -f producer/Dockerfile -t mnist-producer:latest producer

produce: build-producer
	docker run --rm --network=host --name=mnist_producer mnist-producer:latest \
	--filepath data/mnist.npz \
	--entity mnist \
	--limit 3000

build-sinks:
	docker build -f sinks/Dockerfile -t sinks:latest sinks

sink: build-sinks
	docker run --rm --network=host \
	--env MONGO_USER=registry_user \
	--env MONGO_PASSWORD=registry_secret \
	--env MONGO_DATABASE=registry \
	--name=sinks sinks:latest \
	--schema_name featuregroup-mnist  \
	--start_time 2022-12-21T14:16:44 \
	--end_time 2022-12-21T14:16:47 \
	--timestamp_field timestamp \
	--queue_name mnist \

stop:
	docker-compose down

clean: stop
	docker container prune && docker network prune && docker volume prune
