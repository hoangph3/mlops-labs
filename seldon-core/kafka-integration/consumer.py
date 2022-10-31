from kafka import KafkaConsumer
import json


if __name__ == "__main__":
    consumer = KafkaConsumer(
        "cifar10-rest-input",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        # enable_auto_commit=True,
        group_id="test",
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for example in consumer:
        print(example.value)