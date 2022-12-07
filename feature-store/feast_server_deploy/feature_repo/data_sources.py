from feast import KafkaSource, PushSource
from feast.data_format import JsonFormat


mnist_kafka_source = KafkaSource(
    name="mnist_kafka_source",
    kafka_bootstrap_servers="localhost:9092",
    topic="mnist",
    path="data/mnist.parquet",
    timestamp_field="event_timestamp",
    message_format=JsonFormat(
        schema_json="id integer, event_timestamp timestamp, array array, class integer"
    ),
    description="A table describing the mnist features",
    owner="test1@gmail.com"
)

mnist_push_source = PushSource(
    name="mnist_push_source",
    batch_source=mnist_kafka_source
)
