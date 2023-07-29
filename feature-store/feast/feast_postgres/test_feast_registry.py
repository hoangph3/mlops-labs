from feast import RepoConfig, FeatureStore
from feast.repo_config import RegistryConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres import PostgreSQLOfflineStoreConfig

import pandas as pd
from IPython.display import display

# define config
PSQL_HOST = "localhost"
PSQL_PORT = 5432
PSQL_USER = "postgres"
PSQL_PASSWORD = "mysecretpassword"
PSQL_DB = "feast"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

repo_config = RepoConfig(
    registry=RegistryConfig(
        registry_type="sql",
        path=f"postgresql://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}",
    ),
    project="feast_demo_local",
    provider="local",
    offline_store=PostgreSQLOfflineStoreConfig(host=PSQL_HOST, port=PSQL_PORT, database=PSQL_DB,
                                              user=PSQL_USER, password=PSQL_PASSWORD),
    online_store=RedisOnlineStoreConfig(connection_string=f"{REDIS_HOST}:{REDIS_PORT}"),
    entity_key_serialization_version=2,
)

# define store
store = FeatureStore(config=repo_config)

# define entity
entity_df = pd.DataFrame([{"event_id": i} for i in range(10)])
entity_df["event_timestamp"] = pd.to_datetime('now', utc=True)

# fetch feature
feature_v2 = store.get_feature_service("mnist_feature_v2")
training_data = store.get_historical_features(features=feature_v2, entity_df=entity_df)
display(training_data.to_df())

entity_rows = [{"event_id": i} for i in range(10)]
serving_data = store.get_online_features(features=feature_v2, entity_rows=entity_rows)
display(serving_data.to_df())
