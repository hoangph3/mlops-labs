import requests
from typing import Dict
from pyspark.sql.types import StructType

from settings import REGISTRY_HOST


def get_schema(full_schema_name: str) -> Dict:
    r = requests.get(f"http://{REGISTRY_HOST}/schemas/{full_schema_name}")
    return r.json()["properties"]


def get_full_schema_name(schema_type: str, schema_name: str) -> str:
    return f"{schema_type}-{schema_name}"


def get_entity_name(schema_name: str) -> str:
    return get_full_schema_name("entity", schema_name)


def get_featuregroup_name(schema_name: str) -> str:
    return get_full_schema_name("featuregroup", schema_name)


def get_spark_schema(full_schema: str) -> StructType:
    return StructType.fromJson(get_schema(full_schema))
