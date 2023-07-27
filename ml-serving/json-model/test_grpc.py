import requests
import json
import time
import grpc
from mlserver.codecs.string import StringRequestCodec
import mlserver.grpc.converters as converters
import mlserver.grpc.dataplane_pb2_grpc as dataplane
import mlserver.types as types
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

model_name = "json-hello-world"
inputs = {"name": "Foo Bar", "message": "Hello from Client (gRPC)!"}
inputs_bytes = json.dumps(inputs).encode("UTF-8")

inference_request = types.InferenceRequest(
    inputs=[
        types.RequestInput(
            name="echo_request",
            shape=[len(inputs_bytes)],
            datatype="BYTES",
            data=[inputs_bytes],
            parameters=types.Parameters(content_type="str"),
        )
    ]
)

inference_request_g = converters.ModelInferRequestConverter.from_types(
    inference_request, model_name=model_name, model_version=None
)

grpc_channel = grpc.insecure_channel("localhost:8081")
grpc_stub = dataplane.GRPCInferenceServiceStub(grpc_channel)

start_time = time.time()
response = grpc_stub.ModelInfer(inference_request_g)

print(f"full response:\n")
print(response, time.time() - start_time)
# retrive text output as dictionary
inference_response = converters.ModelInferResponseConverter.to_types(response)
raw_json = StringRequestCodec.decode_response(inference_response)
output = json.loads(raw_json[0])
print(f"\ndata part:\n")
pp.pprint(output)