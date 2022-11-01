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

{
   "data" : {
      "ndarray" : [
         [
            0,
            0.1,
            0,
            0,
            0.4,
            0.2,
            0.1,
            0.2,
            0,
            0
         ]
      ],
      "names" : [
         "t:0",
         "t:1",
         "t:2",
         "t:3",
         "t:4",
         "t:5",
         "t:6",
         "t:7",
         "t:8",
         "t:9"
      ]
   },
   "meta" : {
      "requestPath" : {
         "classifier" : "hoangph3/sk_mnist_serving:v0.0.1"
      }
   }
}
```

3. Deploy kafka broker:
```sh
$ helm repo add strimzi http://strimzi.io/charts/
"strimzi" has been added to your repositories

$ kubectl create namespace kafka
namespace/kafka created

$ helm install kafka strimzi/strimzi-kafka-operator --namespace kafka --insecure-skip-tls-verify
NAME: kafka
LAST DEPLOYED: Mon Oct 31 23:09:12 2022
NAMESPACE: kafka
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing strimzi-kafka-operator-0.31.1
To create a Kafka cluster refer to the following documentation.
https://strimzi.io/docs/operators/latest/deploying.html#deploying-cluster-operator-helm-chart-str

$ kubectl apply -f kafka-cluster-config.yaml 
kafka.kafka.strimzi.io/my-cluster created

$ kubectl get pods -n kafka 
NAME                                        READY   STATUS    RESTARTS   AGE
my-cluster-kafka-0                          1/1     Running   0          26s
my-cluster-zookeeper-0                      1/1     Running   0          51s
strimzi-cluster-operator-54cb64cfdd-lhrpl   1/1     Running   0          13m
```

4. Create kafka topics:
```sh
$ kubectl apply -f topics.yaml
kafkatopic.kafka.strimzi.io/cifa10-rest-input created
kafkatopic.kafka.strimzi.io/cifa10-rest-output created
```

5. Deploy another model with kafka:
```sh
$ kubectl apply -f mnist_kafka.yml
kubectl apply -f mnist_kafka.yml
```