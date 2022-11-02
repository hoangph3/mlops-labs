from kafka import KafkaConsumer
import json


if __name__ == "__main__":
    consumer = KafkaConsumer(
        "mnist-rest-output",
        bootstrap_servers=["192.168.0.5:32000"],
        # auto_offset_reset="earliest",
        # enable_auto_commit=True,
        # group_id="test",
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(consumer.topics())
    for example in consumer:
        print(example.value)