from kafka import KafkaConsumer
from seldon_core.proto import prediction_pb2, prediction_pb2_grpc
from seldon_core import utils
from tqdm import tqdm
import argparse
import json
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", type=str, required=True, choices=['rest', 'grpc'],
                        help="proto type")
    args = parser.parse_args()

    if args.proto == 'rest':
        consumer = KafkaConsumer(
        "mnist-rest-input",
        bootstrap_servers=["192.168.0.5:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="test",
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print(consumer.topics())
        for example in tqdm(consumer):
            print(example)
    elif args.proto == 'grpc':
        consumer = KafkaConsumer(
        "mnist-grpc-input",
        bootstrap_servers=["192.168.0.5:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="test",
        # value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print(consumer.topics())
        for example in tqdm(consumer):
            print(example)
    else:
        raise NotImplementedError
