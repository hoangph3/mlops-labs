import json
import time
import argparse
import numpy as np
from datetime import datetime
from loguru import logger
from kafka import KafkaProducer

import settings


def on_send_error(excp: Exception):
    logger.error(f"Error to send record to kafka", exc_info=excp)


def load_mnist_data(data_file):
    with np.load(data_file) as data:
        train_examples = data['x_train']
        train_labels = data['y_train']
    logger.info(f"Load data: {train_examples.shape}, {train_labels.shape}")
    return train_examples, train_labels


def get_topic_name(entity: str) -> str:
    return f"entity-{entity}"


def run(filepath: str, entity: str, limit: int = None) -> int:

    # TODO: register schema on the registry before sending to kafka
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER,
        acks=settings.KAFKA_ACKS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    x_train, y_train = load_mnist_data(filepath)
    for i in range(len(x_train)):
        record = {"x": x_train[i].reshape(-1,).tolist(), "y": int(y_train[i]),
                  "timestamp": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S.%f")}
        producer.send(
            topic=get_topic_name(entity),
            value=record,
            headers=None,
        ).add_errback(on_send_error)

        if i % 1000 == 0:
            logger.info(f"[entity: {entity}] {i} lines were processed")

        if limit and i == limit:
            break

    return i


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature Store Producer")
    parser.add_argument('--filepath', type=str, required=True)
    parser.add_argument('--entity', type=str, required=True)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    run(filepath=args.filepath, entity=args.entity, limit=args.limit)
