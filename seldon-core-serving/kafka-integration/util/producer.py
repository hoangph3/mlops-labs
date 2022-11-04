from kafka import KafkaProducer
from seldon_core import utils
from tqdm import tqdm
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
    producer = KafkaProducer(bootstrap_servers=["127.0.0.1:32100"],
                             value_serializer=lambda x: json.dumps(x).encode("utf-8"))
    for example in tqdm(data):
        line = {"data": {"ndarray": [example.tolist()]}}
        producer.send("mnist-rest-input", line)


def gen_grpc_request(data_file="/home/hoang/Downloads/mnist/data/mnist.npz"):
    data = load_mnist_data(data_file)
    for example in data:
        pass


if __name__ == "__main__":
    gen_rest_request()
