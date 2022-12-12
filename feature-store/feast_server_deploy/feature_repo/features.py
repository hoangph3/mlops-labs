from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Int32, Array, Bytes
from feast import FeatureView, Field
from datetime import timedelta
import pandas as pd
import pickle

from data_sources import mnist_file_source, mnist_request_source, mnist_push_source
from entities import label


mnist_fv = FeatureView(
    name="mnist_feature_view",
    entities=[label],
    ttl=timedelta(days=7),
    schema=[
        Field(name="feature", dtype=Bytes),
    ],
    online=True,
    source=mnist_file_source
)

# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[mnist_fv, mnist_request_source],
    schema=[
        Field(name="norm_feature", dtype=Array(Float32)),
    ],
)
def transformed_inputs(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["norm_feature"] = inputs["feature"]
    return df

# Defines a slightly modified version of the feature view from above, where the source
# has been changed to the push source. This allows fresh features to be directly pushed
# to the online store for this feature view.
mnist_fresh_fv = FeatureView(
    name="mnist_fresh_feature_view",
    entities=[label],
    ttl=timedelta(days=7),
    schema=[
        Field(name="feature", dtype=Bytes),
    ],
    online=True,
    source=mnist_push_source
)

# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[mnist_fresh_fv, mnist_request_source],
    schema=[
        Field(name="norm_feature", dtype=Array(Float32)),
    ],
)
def transformed_fresh_inputs(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["norm_feature"] = inputs["feature"]
    return df