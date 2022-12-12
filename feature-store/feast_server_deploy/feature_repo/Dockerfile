FROM feast-feature-server:latest

RUN pip install "feast[redis,postgres,spark]==0.27.0"

COPY feature_repo/feature_store.yaml feature_store.yaml

# Needed to reach online store within Docker network.
RUN sed -i 's/localhost:6379/feast_redis:6379/g' feature_store.yaml
RUN sed -i 's/127.0.0.1:5432/feast_registry:5432/g' feature_store.yaml
ENV FEAST_USAGE=False

CMD ["feast", "serve", "-h", "0.0.0.0"]
