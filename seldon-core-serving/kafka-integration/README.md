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
$ docker-compose up -d
[+] Running 5/5
 ⠿ Network kafka-integration_default          Created               0.1s
 ⠿ Volume "kafka-integration_kafka_data"      Created               0.0s
 ⠿ Volume "kafka-integration_zookeeper_data"  Created               0.0s
 ⠿ Container zookeeper                        Started               1.0s
 ⠿ Container kafka                            Started               1.9s
```

4. Deploy another mnist model with kafka:

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

$ kubectl get pods -n seldon-model
NAME                                               READY   STATUS    RESTARTS   AGE
mnist-kafka-default-0-classifier-f69f8589c-z46zm   2/2     Running   0          65s
```

5. Send real time data for stream processing, then check the data processed:
```sh
# The bootstrap_servers is 192.168.0.5:9092
$ python3 producer.py --proto rest
50%|████████████████████                    | 30020/60000 [00:32<00:28, 1051.43it/s]

$ python3 consumer.py --proto rest
{'mnist-rest-input', 'mnist-grpc-output', 'mnist-rest-output', 'mnist-grpc-input'}
2345it [00:16, 145.44it/s]

$ kubectl logs -f -n seldon-model mnist-kafka-default-0-classifier-f69f8589c-z46zm seldon-container-engine
{"level":"info","ts":1669906765.922243,"logger":"entrypoint.KafkaServer","msg":"Processed","messages":21000}
{"level":"info","ts":1669906766.4445083,"logger":"entrypoint.KafkaServer","msg":"Ignored","msg":"OffsetsCommitted (<nil>, [mnist-rest-input[0]@21051])"}
{"level":"info","ts":1669906771.4442313,"logger":"entrypoint.KafkaServer","msg":"Ignored","msg":"OffsetsCommitted (<nil>, [mnist-rest-input[0]@21616])"}
```

6. Test model with gRPC:

Create grpc model:
```sh
$ kubectl apply -f mnist_kafka_grpc.yml
```

Send real time data:
```sh
$ python3 producer.py --proto grpc 
```

Get response message:
```sh
$ python3 consumer.py --proto grpc
```
