docker run -it --rm \
    -v $(pwd)/models:/mnt/models \
    -p 9080:9080 \
    seldonio/mlserver:1.3.5-slim
