docker run -it --rm \
    -v $(pwd):/mnt/models \
    -p 8080:8080 \
    -e "MLSERVER_ENV_TARBALL=/mnt/models/faiss.tar.gz" \
    seldonio/mlserver:1.3.5-slim