import json
from time import sleep
import numpy as np

import pandas as pd
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-m",
    "--mode",
    default="setup",
    choices=["setup", "teardown"],
    help="Whether to setup or teardown a Kafka topic with driver stats events. Setup will teardown before beginning emitting events.",
)
parser.add_argument(
    "-b",
    "--bootstrap_servers",
    default="localhost:9092",
    help="Where the bootstrap server is",
)

args = parser.parse_args()


def create_stream(topic_name, servers):
    topic_name = topic_name

    producer = None
    admin = None
    for i in range(20):
        try:
            producer = KafkaProducer(bootstrap_servers=servers)
            admin = KafkaAdminClient(bootstrap_servers=servers)
            print("SUCCESS: instantiated Kafka admin and producer")
            break
        except Exception as e:
            print(
                f"Trying to instantiate admin and producer with bootstrap servers {servers} with error {e}"
            )
            sleep(10)
            pass

    try:
        # Create Kafka topic
        topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
        admin.create_topics([topic])
        print(f"Topic {topic_name} created")
    except Exception as e:
        print(str(e))
        pass

    print("Reading mnist data")
    # load data
    with np.load('mnist.npz') as data:
        train_examples = data['x_train']
        train_labels = data['y_train']
        # test_examples = data['x_test']
        # test_labels = data['y_test']
    data = [{'array': train_examples[i].tolist(), 'class': train_labels[i]} for i in range(len(train_examples))]
    df = pd.DataFrame(data)
    
    # generate timestamp and id entity
    df['event_timestamp'] = pd.to_datetime('now', utc=True)
    df['event_timestamp'] = df['event_timestamp'].astype(str)
    ids = pd.DataFrame(data=list(range(len(df))), columns=["id"])
    df = pd.concat(objs=[df, ids], axis=1)
    print("Emitting events")

    # send data to kafka broker
    for row in df[["id", "event_timestamp", "array", "class"]].to_dict("records"):
        # Make event one more year recent to simulate fresher data
        producer.send(topic_name, json.dumps(row).encode())
        print(row)
        sleep(5.0)


def teardown_stream(topic_name, servers=["localhost:9092"]):
    try:
        admin = KafkaAdminClient(bootstrap_servers=servers)
        print(admin.delete_topics([topic_name]))
        print(f"Topic {topic_name} deleted")
    except Exception as e:
        print(str(e))
        pass


if __name__ == "__main__":
    parsed_args = vars(args)
    mode = parsed_args["mode"]
    servers = parsed_args["bootstrap_servers"]
    teardown_stream("mnist", [servers])
    if mode == "setup":
        create_stream("mnist", [servers])
