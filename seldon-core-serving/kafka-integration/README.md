# Seldon Kafka Integration
In this example we will run SeldonDeployments for a RandomForest Sklearn model which take their inputs from a Kafka topic and push their outputs to a Kafka topic. We will experiment with both REST and gRPC Seldon graphs.

1. Firstly, deploy a randomforest model by applying the seldon manifest shown below:
```sh
$ kubectl apply -f mnist.yml
seldondeployment.machinelearning.seldon.io/mnist-classifier created

$ kubectl get pods -n seldon-model
NAME                                                     READY   STATUS    RESTARTS   AGE
mnist-classifier-default-0-classifier-5cdbd58c5b-9rbh5   3/3     Running   0          76s
```

There are three pods, consist of `classifier`, `istio-proxy` and `seldon-container-engine`.

2. Make a prediction after the Seldon Deployment is available via the ingress gateway:
```sh
$ export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

$ echo $INGRESS_HOST
10.106.254.233

$ curl -X POST http://$INGRESS_HOST/seldon/seldon-model/mnist-classifier/api/v1.0/predictions \
          -H 'Content-Type: application/json' -d @payload.json --noproxy $INGRESS_HOST | json_pp
{"data":{"names":["t:0","t:1","t:2","t:3","t:4","t:5","t:6","t:7","t:8","t:9"],"ndarray":[[0.0,0.1,0.0,0.0,0.4,0.2,0.1,0.2,0.0,0.0]]},"meta":{"requestPath":{"classifier":"hoangph3/sklearn_mnist_classifier:v0.0.1"}}}
```

3. Deploy kafka broker:
```sh
VERSION="0.31.1"
NAMESPACE="kafka"

# create and select a new namespace
$ kubectl create ns $NAMESPACE
$ kubectl config set-context --current --namespace="$NAMESPACE"

# deploy the Strimzi operator
$ curl -L https://github.com/strimzi/strimzi-kafka-operator/releases/download/$VERSION/strimzi-cluster-operator-$VERSION.yaml --insecure | sed "s/namespace: .*/namespace: $NAMESPACE/g" | kubectl replace --force -f -

# deploy the Kafka cluster with external accessing
$ kubectl apply -f kafka-ephemeral.yaml
kafka.kafka.strimzi.io/ephemeral-cluster created

$ kubectl get pods
NAME                                                 READY   STATUS    RESTARTS       AGE
ephemeral-cluster-entity-operator-776554c699-vtclp   3/3     Running   0              101s
ephemeral-cluster-kafka-0                            1/1     Running   0              2m5s
ephemeral-cluster-zookeeper-0                        1/1     Running   0              2m29s
strimzi-cluster-operator-54cb64cfdd-smqrm            1/1     Running   30 (30m ago)   2d13h

# switch to default namespace
$ kubectl config set-context --current --namespace=default

# list service kafka
$ kubectl get svc -n kafka
NAME                                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ephemeral-cluster-kafka-bootstrap            ClusterIP   10.97.202.251    <none>        9091/TCP                     2m17s
ephemeral-cluster-kafka-brokers              ClusterIP   None             <none>        9090/TCP,9091/TCP            2m17s
ephemeral-cluster-kafka-external-0           NodePort    10.105.169.210   <none>        9092:32000/TCP               2m17s
ephemeral-cluster-kafka-external-bootstrap   NodePort    10.105.143.149   <none>        9092:32100/TCP               2m17s
ephemeral-cluster-zookeeper-client           ClusterIP   10.110.6.20      <none>        2181/TCP                     2m41s
ephemeral-cluster-zookeeper-nodes            ClusterIP   None             <none>        2181/TCP,2888/TCP,3888/TCP   2m41s
```

4. Create kafka topics:
```sh
$ kubectl apply -f kafka-topics.yaml
kafkatopic.kafka.strimzi.io/mnist-rest-input created
kafkatopic.kafka.strimzi.io/mnist-rest-output created
```

5. Deploy another mnist model with kafka:

Note that the seldon model can't connect to the kafka broker because the iptables of istio proxy. We should remove proxy first.

```sh
# Show labels for seldon-model namespace
$ kubectl get ns seldon-model --show-labels 
NAME           STATUS   AGE     LABELS
seldon-model   Active   7d13h   istio-injection=enabled,kubernetes.io/metadata.name=seldon-model

# Remove istio-injection label
$ kubectl label ns seldon-model istio-injection-
namespace/seldon-model unlabeled

# Recheck
$ kubectl get ns seldon-model --show-labels
NAME           STATUS   AGE     LABELS
seldon-model   Active   7d13h   kubernetes.io/metadata.name=seldon-model
```

Now we will deploy a model can read real time data:

```sh
$ kubectl apply -f mnist_kafka.yml
```

Note that the address of KAFKA_BROKER in the manifest file can get by the command line: `kubectl get svc -n kafka ephemeral-cluster-kafka-external-bootstrap -o jsonpath -o=jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}'`

```sh
$ kubectl get pods -n seldon-model
NAME                                               READY   STATUS    RESTARTS   AGE
mnist-kafka-default-0-classifier-f69f8589c-z46zm   2/2     Running   0          65s
```

7. Send real time data for stream processing, then check the data processed:
```sh
# The bootstrap_servers is 127.0.0.1:32100, where nodeport is 32100 
$ python3 util/producer.py
50%|████████████████████                    | 30020/60000 [00:32<00:28, 1051.43it/s]

$ python3 util/consumer.py
{'mnist-rest-input', 'mnist-rest-output'}
2345it [00:16, 145.44it/s]
```

8. If you use a external kafka (docker, apache, ...)
- Update `PLAINTEXT` in `KAFKA_ADVERTISED_LISTENERS` in `util/docker-compose.yml` file.
- Deploy kafka: `docker-compose up -d`.
- Update `bootstrap_servers` in `util/producer.py` and `util/consumer.py`.
- Testing:
```sh
$ python3 util/producer.py
50%|████████████████████                    | 30020/60000 [00:32<00:28, 1051.43it/s]

$ python3 util/consumer.py
{'mnist-rest-input', 'mnist-rest-output'}
2345it [00:16, 145.44it/s]
```