# Deploying kafka cluster kubernetes

1. Deploy kafka broker:
```sh
NAMESPACE="kafka"

# create and select a new namespace
$ kubectl create ns $NAMESPACE
$ kubectl config set-context --current --namespace="$NAMESPACE"

# deploy the Strimzi operator
$ kubectl create -f strimzi-cluster-operator-0.31.1.yaml

# deploy the Kafka cluster with external accessing
$ kubectl apply -f kafka-ephemeral.yaml
kafka.kafka.strimzi.io/ephemeral-cluster created

$ kubectl get pods
NAME                                                 READY   STATUS    RESTARTS   AGE
ephemeral-cluster-entity-operator-776554c699-h522h   3/3     Running   0          29s
ephemeral-cluster-kafka-0                            1/1     Running   0          57s
ephemeral-cluster-zookeeper-0                        1/1     Running   0          82s
strimzi-cluster-operator-54cb64cfdd-kbndn            1/1     Running   0          2m36s

# list service kafka
$ kubectl get svc
NAME                                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ephemeral-cluster-kafka-bootstrap            ClusterIP   10.102.159.187   <none>        9091/TCP                     73s
ephemeral-cluster-kafka-brokers              ClusterIP   None             <none>        9090/TCP,9091/TCP            73s
ephemeral-cluster-kafka-external-0           NodePort    10.111.197.45    <none>        9092:32000/TCP               73s
ephemeral-cluster-kafka-external-bootstrap   NodePort    10.103.113.162   <none>        9092:32100/TCP               73s
ephemeral-cluster-zookeeper-client           ClusterIP   10.99.29.241     <none>        2181/TCP                     99s
ephemeral-cluster-zookeeper-nodes            ClusterIP   None             <none>        2181/TCP,2888/TCP,3888/TCP   99s

# switch to default namespace
$ kubectl config set-context --current --namespace=default
```

2. Create kafka topics:
```sh
$ kubectl apply -f kafka-topics.yaml
kafkatopic.kafka.strimzi.io/test-topic created
```

3. Get the address of kafka broker:
```sh
$ kubectl get svc -n kafka ephemeral-cluster-kafka-external-bootstrap -o jsonpath -o=jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}'
10.103.113.162:9092
```

3. Testing:
```sh
# Send data
python3 kafka-client.py --command produce
100%|██████████| 100/100 [00:00<00:00, 18429.21it/s]

# Read data
python3 kafka-client.py --command consume
{'test-topic', '__strimzi-topic-operator-kstreams-topic-store-changelog', '__strimzi_store_topic'}
{'data': 95}
{'data': 96}
{'data': 97}
...
```