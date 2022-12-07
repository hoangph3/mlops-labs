# Importing dependencies
from datetime import timedelta
from feast import Field, FeatureView
from feast.types import Float32, Array, Int32

from entities import *
from data_sources import *


mnist_feature_view = FeatureView(
    name="mnist_feature_view",
    ttl=timedelta(seconds=86400 * 365),
    entities=[event_id],
    schema=[
        Field(name="array", dtype=Array(Float32)),
        Field(name="class", dtype=Int32)
        ],    
    source=mnist_push_source,
    online=True,
    owner="test2@gmail.com"
)
