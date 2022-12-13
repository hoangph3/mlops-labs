from feast import PushSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)


# Read data from postgres database
mnist_postgres_source = PostgreSQLSource(
    name="mnist_postgres_source",
    query="SELECT * FROM feast_mnist",
    timestamp_field="event_timestamp",
)

# Defines a way to push data (to be available offline, online or both) into Feast.
mnist_push_source = PushSource(
    name="mnist_push_source",
    batch_source=mnist_postgres_source,
)
