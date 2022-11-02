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

$ kubectl get pods
NAME                                          READY   STATUS    RESTARTS       AGE
my-cluster-entity-operator-6b9c8fb54f-5kq7f   3/3     Running   0              3m21s
my-cluster-kafka-0                            1/1     Running   0              3m45s
my-cluster-zookeeper-0                        1/1     Running   0              4m9s
strimzi-cluster-operator-54cb64cfdd-smqrm     1/1     Running   7 (125m ago)   24h

# switch to default namespace
$ kubectl config set-context --current --namespace=default

# list service kafka
$ kubectl get svc -n kafka
NAME                                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
my-cluster-kafka-bootstrap            ClusterIP   10.96.132.51   <none>        9091/TCP                     4m10s
my-cluster-kafka-brokers              ClusterIP   None           <none>        9090/TCP,9091/TCP            4m10s
my-cluster-kafka-external-0           NodePort    10.98.47.184   <none>        9092:32000/TCP               4m10s
my-cluster-kafka-external-bootstrap   NodePort    10.108.70.39   <none>        9092:32100/TCP               4m10s
my-cluster-zookeeper-client           ClusterIP   10.97.94.160   <none>        2181/TCP                     4m34s
my-cluster-zookeeper-nodes            ClusterIP   None           <none>        2181/TCP,2888/TCP,3888/TCP   4m34s
```

4. Create kafka topics:
```sh
$ kubectl apply -f kafka-topics.yaml
```

5. Deploy another mnist model with kafka:
```sh
$ kubectl apply -f mnist_kafka.yml
```
Note that the address of KAFKA_BROKER in the manifest file can get by the command line: `$(minikube ip):$(kubectl get svc -n kafka my-cluster-kafka-external-0 -o=jsonpath='{.spec.ports[0].nodePort}')`
```
$ kubectl get pods -n seldon-model 
NAME                                                     READY   STATUS    RESTARTS      AGE
mnist-classifier-default-0-classifier-7b6769bfcd-6wb4j   3/3     Running   12 (8h ago)   25h
mnist-kafka-default-0-classifier-6cd8445dd7-42cd9        3/3     Running   0             2m19s
```

6. Send real time data for stream processing, then check the data processed:
```
$ python3 util/producer.py
$ python3 util/consumer.py
```