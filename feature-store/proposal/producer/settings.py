import os


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_ACKS = os.getenv("KAFKA_ACKS", "all")
