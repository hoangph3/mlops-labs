import requests
import json
import time
from mlserver.types import InferenceResponse
from mlserver.codecs.string import StringRequestCodec
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

inputs = {"name": "Foo Bar", "message": "Hello from Client (REST)!"}

# NOTE: this uses characters rather than encoded bytes. It is recommended that you use the `mlserver` types to assist in the correct encoding.
inputs_string = json.dumps(inputs)

inference_request = {
    "inputs": [
        {
            "name": "echo_request",
            "shape": [len(inputs_string)],
            "datatype": "BYTES",
            "data": [inputs_string],
        }
    ]
}

endpoint = "http://localhost:8080/v2/models/json-hello-world/infer"

start_time = time.time()
response = requests.post(endpoint, json=inference_request)

print(f"full response:\n")
print(response, time.time() - start_time)
# retrive text output as dictionary
inference_response = InferenceResponse.parse_raw(response.text)
raw_json = StringRequestCodec.decode_response(inference_response)
output = json.loads(raw_json[0])
print(f"\ndata part:\n")
pp.pprint(output)