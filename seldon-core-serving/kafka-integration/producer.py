from kafka import KafkaProducer
from seldon_core import utils
from seldon_core.proto import prediction_pb2, prediction_pb2_grpc
import tensorflow as tf
from tqdm import tqdm
import argparse
import numpy as np
import json
import grpc


def load_mnist_data(data_file):
    with np.load(data_file) as data:
        train_examples = data['x_train']
        train_labels = data['y_train']
        test_examples = data['x_test']
        test_labels = data['y_test']
    input_shape = (-1, 784)
    train_examples = train_examples.reshape(input_shape)
    print("Load data:", np.shape(train_examples))
    return train_examples


def gen_rest_request(data_file="/home/hoang/Downloads/mnist/data/mnist.npz"):
    data = load_mnist_data(data_file)
    producer = KafkaProducer(bootstrap_servers=["192.168.0.5:9092"],
                             value_serializer=lambda x: json.dumps(x).encode("utf-8"))
    for example in tqdm(data):
        line = {"data": {"ndarray": [example.tolist()]}}
        producer.send("mnist-rest-input", line)
        break


def gen_grpc_request(data_file="/home/hoang/Downloads/mnist/data/mnist.npz"):
    data = load_mnist_data(data_file)
    producer = KafkaProducer(bootstrap_servers=["192.168.0.5:9092"])
    for example in tqdm(data):
        datadef = utils.array_to_grpc_datadef(data_type='ndarray', array=example)
        request = prediction_pb2.SeldonMessage(data=datadef)
        data_str = request.SerializeToString()
        producer.send("mnist-grpc-input",
                      value=data_str)
        break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", type=str, required=True, choices=['rest', 'grpc'],
                        help="proto type")
    args = parser.parse_args()

    if args.proto == 'rest':
        gen_rest_request()
    elif args.proto == 'grpc':
        gen_grpc_request()
    else:
        raise NotImplementedError
