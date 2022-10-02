from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import predict_pb2
import tensorflow as tf
import requests
import grpc
import base64
import json
import time


data = tf.io.read_file("images/grace_hopper.jpg").numpy()


def predict_grpc(batch_size=10):
    # define host
    channel = grpc.insecure_channel("localhost:8500")
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    # generate request
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'resnet'
    request.model_spec.signature_name = 'serving_preprocess'
    request.inputs["raw_images"].CopyFrom(
                tf.make_tensor_proto([data] * batch_size, dtype=tf.string)
            )
    result = stub.Predict(request, 30.0)
    return result


def predict_rest_api(batch_size=10):
    url = "http://localhost:8501/v1/models/resnet/versions/101:predict"
    image_b64str = base64.b64encode(data).decode('utf-8')
    json_data = {
        "signature_name": "serving_preprocess",
        "instances": [{"b64": image_b64str}] * batch_size
    }
    response = requests.post(url=url, json=json_data)
    return json.loads(response.text)


if __name__ == "__main__":
    # handle out of memory
    n_batch = 5
    batch_size = 50
    print("========== Test on {} records ==========".format(n_batch * batch_size))

    # test gRPC
    start = time.time()
    for _ in range(n_batch):
        try:
            predict_grpc(batch_size)
        except Exception as e:
            print("Error gRPC: {}".format(e))
    print("Predict gRPC in {}s".format(time.time() - start))

    # test REST api
    start = time.time()
    for _ in range(n_batch):
        try:
            predict_rest_api(batch_size)
        except Exception as e:
            print("Error REST api: {}".format(e))
    print("Predict REST api in {}s".format(time.time() - start))
