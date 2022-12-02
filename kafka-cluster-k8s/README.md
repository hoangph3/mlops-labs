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

Note that the address of KAFKA_BROKER in the manifest file can get by the command line: `kubectl get svc -n kafka ephemeral-cluster-kafka-external-bootstrap -o jsonpath -o=jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}'`