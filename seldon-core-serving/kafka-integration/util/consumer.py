from kafka import KafkaConsumer
from tqdm import tqdm
import json
import time


if __name__ == "__main__":
    consumer = KafkaConsumer(
        "mnist-rest-output",
        bootstrap_servers=["127.0.0.1:32100"],
        # auto_offset_reset="earliest",
        # enable_auto_commit=True,
        # group_id="test",
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(consumer.topics())
    for example in tqdm(consumer):
        pass