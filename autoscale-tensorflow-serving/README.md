### Autoscaling Tensorflow model with Kubernetes

Serving deep learning models can be especially challenging. The models are often large, requiring gigabytes of memory. They are also very compute intensive - a small number of concurrent requests can fully utilize a CPU or GPU. Automatic horizontal scaling is one of the primary strategies used in architecting scalable and reliable model serving infrastructures for deep learning models.

Firstly, we need to deploy a dummy tensorflow model. In this case we use Resnet101 pretrained model.

Create the `tf-serving` namespace:
```sh
$ kubectl create ns tf-serving
namespace/tf-serving created
```

Create the ConfigMap from the `configmap-resnet101.yaml` manifest file:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: resnet101-configs
  namespace: tf-serving
data:
  MODEL_NAME: image_classifier
  MODEL_PATH: /models/resnet101
```
```sh
$ kubectl apply -f configmap-resnet101.yaml
configmap/resnet101-configs created
```

Create the ResNet101 deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-classifier-resnet101
  namespace: tf-serving
  labels:
    app: image-classifier
    version: resnet101
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-classifier
      version: resnet101
  template:
    metadata:
      labels:
        app: image-classifier
        version: resnet101
    spec:
      containers:
      - name: tf-serving
        image: "tensorflow/serving:2.5.1"
        args: 
        - "--model_name=$(MODEL_NAME)"
        - "--model_base_path=$(MODEL_PATH)" 
        envFrom:
        - configMapRef:
            name: resnet101-configs
        imagePullPolicy: IfNotPresent
        readinessProbe:
          tcpSocket:
            port: 8500
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 10
        ports:
        - name: http
          containerPort: 8501
          protocol: TCP
        - name: grpc
          containerPort: 8500
          protocol: TCP
        resources:
          requests:
            cpu: "0.5"
            memory: 1Gi
        volumeMounts:
        - name: model
          mountPath: /models/resnet101
      volumes:
      - name: model
        hostPath: 
          path: /home/hoang/Downloads/resnet101
```
```sh
$ kubectl apply -f deployment-resnet101.yaml
deployment.apps/image-classifier-resnet101 created

$ kubectl get deployments.apps -n tf-serving
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
image-classifier-resnet101   1/1     1            1           6m27s
```

Exposing the deployment to service:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: image-classifier
  namespace: tf-serving
  labels:
    app: image-classifier
spec:
  type: LoadBalancer
  ports:
  - port: 8500
    protocol: TCP
    name: tf-serving-grpc
  - port: 8501
    protocol: TCP
    name: tf-serving-http
  selector:
    app: image-classifier
```
```sh
$ kubectl apply -f service.yaml
service/image-classifier created

$ kubectl get svc -n tf-serving 
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
image-classifier   LoadBalancer   10.101.25.178   <pending>     8500:31261/TCP,8501:31055/TCP   18s

$ minikube tunnel

$ kubectl get svc -n tf-serving
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                         AGE
image-classifier   LoadBalancer   10.101.25.178   10.101.25.178   8500:31261/TCP,8501:31055/TCP   43s
```

The final step is to add Horizontal Pod Autoscaler (HPA). The command below configures HPA to start a new replica of TensorFlow Serving whenever the mean CPU utilization across all already running replicas reaches `60%`. HPA will attempt to create up to 4 replicas and scale down to 1 replica.

```sh
$ kubectl autoscale deployment image-classifier-resnet101 -n tf-serving \
--cpu-percent=60 \
--min=1 \
--max=4
horizontalpodautoscaler.autoscaling/image-classifier-resnet101 autoscaled

$ kubectl get hpa -n tf-serving 
NAME                         REFERENCE                               TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
image-classifier-resnet101   Deployment/image-classifier-resnet101   <unknown>/60%   1         4         1          25s
```

We get `<unknown>/60%` value in the `TARGETS`. Is there anything wrong? Let's describe the `horizontalpodautoscaler.autoscaling`.

```sh
$ kubectl describe horizontalpodautoscalers.autoscaling -n tf-serving image-classifier-resnet101
...
Events:
  Type     Reason                        Age   From                       Message
  ----     ------                        ----  ----                       -------
  Warning  FailedGetResourceMetric       13s   horizontal-pod-autoscaler  failed to get cpu utilization: missing request for cpu
  Warning  FailedComputeMetricsReplicas  13s   horizontal-pod-autoscaler  invalid metrics (1 invalid out of 1), first error is: failed to get cpu utilization: missing request for cpu

$ kubectl top nodes
error: Metrics API not available
```

We must install the `metrics-server`, note that we need to add `--kubelet-insecure-tls` under `spec.template.spec.containers.args` to disable certificate validation.
```sh
$ kubectl apply -f metrics-server.yaml 
serviceaccount/metrics-server created
clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
clusterrole.rbac.authorization.k8s.io/system:metrics-server created
rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader created
clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator created
clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server created
service/metrics-server created
deployment.apps/metrics-server created
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created

$ kubectl get pods -n kube-system metrics-server-df6668697-nvg6c
NAME                             READY   STATUS    RESTARTS   AGE
metrics-server-df6668697-nvg6c   1/1     Running   0          20m

$ kubectl top nodes
NAME           CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
jump-windows   1143m        28%    6777Mi          68%
```

Now re-create the hpa and describe it:
```sh
$ kubectl get hpa -n tf-serving
NAME                         REFERENCE                               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
image-classifier-resnet101   Deployment/image-classifier-resnet101   0%/60%    1         4         1          17m

$ kubectl describe hpa -n tf-serving image-classifier-resnet101
...
Events:
  Type    Reason             Age   From                       Message
  ----    ------             ----  ----                       -------
  Normal  SuccessfulRescale  10m   horizontal-pod-autoscaler  New size: 1; reason: All metrics below target
```

Testing the model with sample request body `locust/request-body.json`:
```sh
$ EXTERNAL_IP=10.101.25.178
$ curl -d @locust/request-body.json -X POST http://${EXTERNAL_IP}:8501/v1/models/image_classifier/versions/1:predict
{
    "predictions": [[
      ...
      ]
    ]
}
```

We are now ready to load test the ResNet101, we will use an open source load testing tool Locust to generate prediction requests.

Install locust:
```sh
$ pip3 install locust
$ locust -V
locust 1.4.1
$ locust
Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.
```

The locust folder contains the Locust script that generates prediction requests against the ResNet101 model. The script uses the same request body you used previously to verify the TensorFlow Serving deployment. The script is configured to progressively increase the number of simulated users that send prediction requests to the ResNet101 model. After reaching the maximum number of configured users, the script stops generating the load. The number of users is adjusted every 60s.

To start the test, execute the command:
```sh
$ cd locust
$ locust -f tasks.py --host http://${EXTERNAL_IP}:8501
...
[2022-09-30 21:07:01,259] jump-windows/INFO/locust.main: Starting web interface at http://0.0.0.0:8089 (accepting connections from all network interfaces)
[2022-09-30 21:07:01,266] jump-windows/INFO/locust.main: Starting Locust 1.4.1
```

Open your favorite browser, and access to the address: http://0.0.0.0:8089, then Start swarming.

Within a minute or so, you should see the higher CPU load; for example:
```sh
$ kubectl get hpa -n tf-serving image-classifier-resnet101 -w
NAME                         REFERENCE                               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
image-classifier-resnet101   Deployment/image-classifier-resnet101   426%/60%   1         4         1          24m
image-classifier-resnet101   Deployment/image-classifier-resnet101   215%/60%   1         4         4          24m
```

Here, CPU consumption has increased to 215% of the request. As a result, the Deployment was resized to 4 replicas:
```sh
$ kubectl get deployment -n tf-serving image-classifier-resnet101 
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
image-classifier-resnet101   4/4     4            4           29m
```

Stop sending the load by typing `<Ctrl> + C` in the locust terminal screen.

Then verify the result state (after a minute or so):
```sh
$ kubectl get hpa -n tf-serving image-classifier-resnet101 -w
NAME                         REFERENCE                               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
image-classifier-resnet101   Deployment/image-classifier-resnet101   0%/60%     1         4         4          27m
image-classifier-resnet101   Deployment/image-classifier-resnet101   0%/60%     1         4         1          32m
```

and the Deployment also shows that it has scaled down:
```sh
$ kubectl get deploy -n tf-serving image-classifier-resnet101 
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
image-classifier-resnet101   1/1     1            1           36m
```
Once CPU utilization dropped to 0, the HPA automatically scaled the number of replicas back down to 1. Autoscaling the replicas may take a few minutes.