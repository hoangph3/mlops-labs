from tensorflow_serving.apis import prediction_log_pb2
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import model_pb2
import tensorflow as tf
import numpy as np
import os


SERVING_DIR = "/home/hoang/Downloads/resnet_serving"
inputs = np.random.rand(1, 224, 224, 3)
n_samples = 500

def main():
    for version in os.listdir(SERVING_DIR):
        warmup_dir = os.path.join(SERVING_DIR, version, "assets.extra")
        if not os.path.exists(warmup_dir):
            os.makedirs(warmup_dir)

        with tf.io.TFRecordWriter(os.path.join(warmup_dir, "tf_serving_warmup_requests")) as writer:
            request = predict_pb2.PredictRequest(
                model_spec=model_pb2.ModelSpec(name="resnet"),
                inputs={"model_input": tf.make_tensor_proto(inputs, shape=inputs.shape, dtype=np.float32)}
                )
            log = prediction_log_pb2.PredictionLog(
                predict_log=prediction_log_pb2.PredictLog(request=request))
            for _ in range(n_samples):
                writer.write(log.SerializeToString())
    return

if __name__ == "__main__":
    main()