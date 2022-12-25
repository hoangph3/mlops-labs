from feast import FeatureView, Field
from feast.types import String
from datetime import timedelta

from data_sources import mnist_postgres_source, mnist_push_source
from entities import event_id


mnist_fv = FeatureView(
    name="mnist_feature_view",
    entities=[event_id],
    ttl=timedelta(seconds=86400 * 10000),
    schema=[
        Field(name="feature", dtype=String),
    ],
    online=True,
    source=mnist_postgres_source
)

# Defines a slightly modified version of the feature view from above, where the source
# has been changed to the push source. This allows fresh features to be directly pushed
# to the online store for this feature view.
mnist_fresh_fv = FeatureView(
    name="mnist_fresh_feature_view",
    entities=[event_id],
    ttl=timedelta(seconds=86400 * 10000),
    schema=[
        Field(name="feature", dtype=String),
    ],
    online=True,
    source=mnist_push_source
)
