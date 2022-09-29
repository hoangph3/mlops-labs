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
            cpu: "2"
            memory: 4Gi
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

At start, each replica requests 2CPUs and 4GB of RAM. Because my cluster is configured with 3CPUs and 10GB or RAM. It means that only a single replica can run on a node.

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
  type: NodePort
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
NAME               TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                         AGE
image-classifier   NodePort   10.108.65.64   <none>        8500:31048/TCP,8501:30904/TCP   24s
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
image-classifier-resnet101   Deployment/image-classifier-resnet101   <unknown>/60%   1         4         1          48s
```

Testing the model with sample request body `locust/request-body.json`:
```sh
NODEPORT_IP=$(minikube ip)
curl -d @locust/request-body.json -X POST http://${NODEPORT_IP}:30904/v1/models/image_classifier/versions/1:predict
```