import os


KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "localhost:9092")

MONGO_USER = os.getenv("MONGO_USER", "registry_user")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "registry_secret")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "registry")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
REGISTRY_HOST: str = os.getenv("REGISTRY_HOST", "localhost:8000")


def get_mongo_uri():
    return f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"
