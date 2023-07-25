import requests
from train import _load_ds
from mlserver.types import InferenceRequest
from mlserver.codecs import NumpyCodec
from utils import plot
import numpy as np

# URL
inference_url = "http://localhost:9080/v2/models/mnist/infer"

# Convert the TensorFlow tensor to a numpy array
dataset = _load_ds(batch_size=16)
for x, y in dataset:
    input_data = x.numpy()
    labels = y.numpy()
    break

# Build the inference request
inference_request = InferenceRequest(
    inputs=[
        NumpyCodec.encode_input(name="payload", payload=input_data)
    ]
)

# Send the inference request and capture response
print("Sending Inference Request...")
res = requests.post(inference_url, json=inference_request.dict())
print("Got Response...")

# Parse the JSON string into a Python dictionary
response_dict = res.json()

# Extract the data array and shape from the output, assuming only one output or the target output is at index 0
print(response_dict)
data_list = response_dict["outputs"][0]["data"]
data_shape = response_dict["outputs"][0]["shape"]

# Convert the data list to a numpy array and reshape it
data_array = np.array(data_list).reshape(data_shape)
print("Predictions:", data_array)

# Plot the examples with their predictions
plot(input_data, labels, data_array)
