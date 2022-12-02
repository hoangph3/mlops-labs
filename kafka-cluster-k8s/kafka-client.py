import argparse
import json
from kafka import KafkaConsumer, KafkaProducer
from tqdm import tqdm

_KAKFA_BROKER = "10.103.113.162:9092"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=str, required=True, choices=['produce', 'consume'])
    args = parser.parse_args()
    
    if args.command == 'produce':
        producer = KafkaProducer(bootstrap_servers=[_KAKFA_BROKER],
                                value_serializer=lambda x: json.dumps(x).encode("utf-8"))
        for i in tqdm(range(100)):
            data = {'data': i}
            producer.send("test-topic", data)
    elif args.command == 'consume':
        consumer = KafkaConsumer("test-topic",
                                bootstrap_servers=[_KAKFA_BROKER],
                                auto_offset_reset="earliest",
                                enable_auto_commit=True,
                                group_id="user_test",
                                value_deserializer=lambda x: json.loads(x.decode('utf-8')))
        print(consumer.topics())
        for example in tqdm(consumer):
            print(example.value)
    else:
        raise NotImplementedError