from feast import FileSource, RequestSource, PushSource, Field
from feast.types import Int32


# Read data from parquet files. Parquet is convenient for local development mode. For
# production, you can use your favorite DWH, such as BigQuery. See Feast documentation
# for more info.
mnist_file_source = FileSource(
    name="mnist_file_source",
    path="data/mnist.parquet",
    timestamp_field="event_timestamp",
)

# Define a request data source which encodes features / information only
# available at request time (e.g. part of the user initiated HTTP request)
mnist_request_source = RequestSource(
    name="mnist_request_source",
    schema=[
        Field(name="norm_value", dtype=Int32),
    ]
)

# Defines a way to push data (to be available offline, online or both) into Feast.
mnist_push_source = PushSource(
    name="mnist_push_source",
    batch_source=mnist_file_source,
)