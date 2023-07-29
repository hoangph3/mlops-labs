## Feature Store Pipeline

1. Deploy pipeline:
```sh
docker-compose up -d --build
```

2. Access the UI:

* [Jupyter lab](http://localhost:8888) (get token from `docker logs -f pyspark-notebook`)
* [Minio console](http://localhost:9000)

3. Clean:
```sh
docker-compose down -v
```