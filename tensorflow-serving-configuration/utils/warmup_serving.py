from tensorflow_serving.apis import prediction_log_pb2
from tensorflow_serving.apis import predict_pb2
import tensorflow as tf
import os


SERVING_DIR = "/home/hoang/Downloads/resnet_serving"
image_bytes = tf.io.read_file("images/grace_hopper.jpg").numpy()
n_records = 200


def warmup_serving():
    for version in os.listdir(SERVING_DIR):
        warmup_dir = os.path.join(SERVING_DIR, version, "assets.extra")
        if not os.path.exists(warmup_dir):
            os.makedirs(warmup_dir)

        with tf.io.TFRecordWriter(os.path.join(warmup_dir, "tf_serving_warmup_requests")) as writer:
            request = predict_pb2.PredictRequest()
            request.model_spec.name = "resnet"
            request.model_spec.signature_name = "serving_preprocess"
            request.inputs["raw_images"].CopyFrom(
                tf.make_tensor_proto([image_bytes], dtype=tf.string)
            )
            log = prediction_log_pb2.PredictionLog(
                predict_log=prediction_log_pb2.PredictLog(request=request))
            for _ in range(n_records):
                writer.write(log.SerializeToString())
    return

if __name__ == "__main__":
    warmup_serving()