from tqdm import tqdm
import argparse
import pymongo
import redis
import json

import settings


def run(schema_name: str, timestamp_field: str,
        start_time: str, end_time: str,
        queue_name: str):
    
    # connect to db
    db_uri = settings.get_mongo_uri()
    db_client = pymongo.MongoClient(db_uri)
    db = db_client[settings.MONGO_DATABASE]
    collection = db[schema_name]

    # query
    query = {
        timestamp_field: {"$gte": start_time, "$lte": end_time},
    }
    result = collection.find(query, {"_id": 0})

    # connect to redis
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    for res in tqdm(result, desc="Sink"):
        redis_client.lpush(queue_name, json.dumps(res))
    
    # close connection
    db_client.close()
    redis_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature Store Sinks")
    parser.add_argument('--schema_name', type=str, required=True)
    parser.add_argument('--timestamp_field', type=str, required=True)
    parser.add_argument('--start_time', type=str)
    parser.add_argument('--end_time', type=str)
    parser.add_argument('--queue_name', type=str, required=True)
    args = parser.parse_args()
    run(
        schema_name=args.schema_name,
        timestamp_field=args.timestamp_field,
        start_time=args.start_time,
        end_time=args.end_time,
        queue_name=args.queue_name
    )
