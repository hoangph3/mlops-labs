### Deploying TensorFlow model as Canary Releases Kubernetes and Istio

In this lab, we will use Istio with Minikube and TensorFlow Serving to create canary deployments of TensorFlow machine learning models. More concretely, we will:
1. Prepare a minikube cluster with the Istio add-on for TensorFlow Serving.
2. Create a canary release of a TensorFlow model deployment.
3. Configure various traffic splitting strategies.

Suppose we have already with minikube cluster look like that below:
```sh
$ minikube profile list
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
| Profile  | VM Driver | Runtime |     IP      | Port | Version | Status  | Nodes | Active |
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
| minikube | none      | docker  | 192.168.0.5 | 8443 | v1.24.3 | Running |     1 | *      |
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
```

Let's download istio from https://github.com/istio/istio/releases/ and extracting:
```sh
$ wget https://github.com/istio/istio/releases/download/1.12.7/istio-1.12.7-linux-amd64.tar.gz

$ tar zvxf istio-1.12.7-linux-amd64.tar.gz

$ cd istio-1.12.7 && ls
bin  LICENSE  manifests  manifest.yaml  README.md  samples  tools

$ export PATH=$PWD/bin:$PATH

$ istioctl install
This will install the Istio 1.12.7 default profile with ["Istio core" "Istiod" "Ingress gateways"] components into the cluster. Proceed? (y/N) y
✔ Istio core installed
✔ Istiod installed- Processing resources for Ingress gateways. Waiting for Deployment/istio-system/istio-ingressgateway
✔ Ingress gateways installed
✔ Installation complete
Making this installation the default for injection and validation.
```

Now listing pods in `istio-system` namespace
```sh
$ kubectl get pods -n istio-system
NAME                                    READY   STATUS    RESTARTS   AGE
istio-ingressgateway-58fbb84dfd-d79rj   1/1     Running   0          15m
istiod-77f69cccd6-t9grw                 1/1     Running   0          16m

$ kubectl get svc -n istio-system istio-ingressgateway
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                                      AGE
istio-ingressgateway   LoadBalancer   10.110.24.130   <pending>     15021:30487/TCP,80:30717/TCP,443:32359/TCP   24h
```

Because my environment does not provide an external load balancer for the ingress gateway, so we see the `EXTERNAL-IP` have `<pending>` status. Let's use `minikube tunnel` to fix this.

```sh
$ minikube tunnel 
Status:	
	machine: minikube
	pid: 24042
	route: 10.96.0.0/12 -> 192.168.0.5
	minikube: Running
	services: [istio-ingressgateway]
    errors: 
		minikube: no errors
		router: no errors
		loadbalancer emulator: no errors

$ kubectl get svc -n istio-system istio-ingressgateway
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                                      AGE
istio-ingressgateway   LoadBalancer   10.110.24.130   10.110.24.130   15021:30487/TCP,80:30717/TCP,443:32359/TCP   25h
```

Create the `tf-serving` namespace and enable automatic proxy sidecar injection.
```sh
$ kubectl create ns tf-serving
namespace/tf-serving created

$ kubectl label ns tf-serving istio-injection=enabled
namespace/tf-serving labeled

$ kubectl get ns --show-labels
NAME              STATUS   AGE   LABELS
default           Active   13d   kubernetes.io/metadata.name=default
istio-system      Active   20m   kubernetes.io/metadata.name=istio-system
kube-flannel      Active   13d   kubernetes.io/metadata.name=kube-flannel,pod-security.kubernetes.io/enforce=privileged
kube-node-lease   Active   13d   kubernetes.io/metadata.name=kube-node-lease
kube-public       Active   13d   kubernetes.io/metadata.name=kube-public
kube-system       Active   13d   kubernetes.io/metadata.name=kube-system
tf-serving        Active   57s   istio-injection=enabled,kubernetes.io/metadata.name=tf-serving
```

Download ResNet50 pretrained model using python code:
```python
>>> import tensorflow as tf

>>> print(tf.__version__)
2.6.2

>>> model = tf.keras.applications.resnet50.ResNet50()
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet50_weights_tf_dim_ordering_tf_kernels.h5
102973440/102967424 [==============================] - 32s 0us/step

>>> model.save('/home/hoang/Downloads/resnet50/1') # 1 is version
INFO:tensorflow:Assets written to: /home/hoang/Downloads/resnet50/1/assets
```

So we have the ResNet50 pretrained model:
```sh
$ ls -la resnet50/1/
total 4076
drwxrwxrwx 1 hoang hoang    4096 Thg 9 24 23:08 .
drwxrwxrwx 1 hoang hoang    4096 Thg 9 24 22:56 ..
drwxrwxrwx 1 hoang hoang       0 Thg 9 24 23:08 assets
-rwxrwxrwx 1 hoang hoang  365902 Thg 9 24 23:08 keras_metadata.pb
-rwxrwxrwx 1 hoang hoang 3796233 Thg 9 24 23:08 saved_model.pb
drwxrwxrwx 1 hoang hoang       0 Thg 9 24 23:08 variables
```

Creating ConfigMap `configmap-resnet50.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: resnet50-configs
  namespace: tf-serving
data:
  MODEL_NAME: image_classifier
  MODEL_PATH: /models/resnet50
```

Using `kubectl` create the ConfigMap:
```sh
$ kubectl apply -f configmap-resnet50.yaml
configmap/resnet50-configs created
```

Creating the deployment `deployment-resnet50.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-classifier-resnet50
  namespace: tf-serving
  labels:
    app: image-classifier
    version: resnet50
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-classifier
      version: resnet50
  template:
    metadata:
      labels:
        app: image-classifier
        version: resnet50
    spec:
      containers:
      - name: tf-serving
        image: "tensorflow/serving:2.5.1"
        args: 
        - "--model_name=$(MODEL_NAME)"
        - "--model_base_path=$(MODEL_PATH)" 
        envFrom:
        - configMapRef:
            name: resnet50-configs
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8501
          protocol: TCP
        - name: grpc
          containerPort: 8500
          protocol: TCP
        volumeMounts:
        - name: model
          mountPath: /models/resnet50
      volumes:
      - name: model
        hostPath: 
          path: /home/hoang/Downloads/resnet50
```

Create the deployment and inspect it:
```sh
$ kubectl apply -f deployment-resnet50.yaml 
deployment.apps/image-classifier-resnet50 created

$ kubectl get deployments.apps -n tf-serving 
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
image-classifier-resnet50   1/1     1            1           91s

$ kubectl get pods -n tf-serving 
NAME                                        READY   STATUS    RESTARTS   AGE
image-classifier-resnet50-8556494d8-q4qm7   2/2     Running   0          5s
```

Notice that the deployment is annotated with two labels: `app: image-classifier` and `version: resnet50`. These labels will be the key when configuring Istio traffic routing.

Creating the service manifest in `service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: image-classifier
  namespace: tf-serving
  labels:
    app: image-classifier
    service: image-classifier
spec:
  type: ClusterIP
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

The selector field refers to the `app: image-classifier` label. What it means is that the service will load balance across all pods annotated with this label. At this point these are the pods comprising the ResNet50 deployment. The service type is `ClusterIP`. The IP address exposed by the service is only visible within the cluster.

Create the service and inspect it:
```sh
$ kubectl apply -f service.yaml
service/image-classifier created

$ kubectl get svc -n tf-serving 
NAME               TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)             AGE
image-classifier   ClusterIP   10.96.44.45   <none>        8500/TCP,8501/TCP   12s
```

Now we use an Istio Ingress gateway to manage inbound and outbound traffic for your mesh.

Firstly, configure the gateway to open port `80` for the `HTTP` traffic:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: image-classifier-gateway
  namespace: tf-serving
spec:
  selector:
    istio: ingressgateway 
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

```sh
$ kubectl apply -f gateway.yaml
gateway.networking.istio.io/image-classifier-gateway created

$ kubectl get gateways.networking.istio.io -n tf-serving 
NAME                       AGE
image-classifier-gateway   1s
```

At this point the gateway is running but your ResNet50 deployment is still not accessible from the outside of the cluster. We need to configure a virtual service.

`Virtual services`, along with destination rules are the key building blocks of Istio's traffic routing functionality. A virtual service lets you configure how requests are routed to a service within an Istio service mesh. Each virtual service consists of a set of routing rules that are evaluated in order, letting Istio match each given request to the virtual service to a specific real destination within the mesh.

We will start by configuring a virtual service that forwards all requests sent through the gateway on port `80` to the `image-classifier` service on port `8501`.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: image-classifier
  namespace: tf-serving
spec:
  hosts:
  - "*"
  gateways:
  - image-classifier-gateway
  http:
  - route:
    - destination:
        host: image-classifier
        port:
          number: 8501
```

Recall that the `image-classifier` service is configured to load balance between pods annotated with the `app: image-classifer` label. As a result all requests sent to the gateway will be forwarded to the ResNet50 deployment.

```sh
$ kubectl apply -f virtual-service.yaml 
virtualservice.networking.istio.io/image-classifier created
```

Now we will test access to the ResNet50 model.

```sh
$ kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
10.110.24.130

$ kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}'
80
```

Now we will generate the inputs of ResNet50 model from image:

![](test.jpeg)

```sh
$ python3 gen_payload.py
```

You will see the `request-body.json` file have created. Using `curl` or requests module in python3 command to send request to serving model.

```sh
$ curl -d @request-body.json -X POST http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict
{
    "predictions": [[
      ...
      ]
    ]
}
```

```python
>>> import requests, json, numpy
>>> r = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                      json=json.load(open("request-body.json")))
>>> res = r.json()
>>> preds = res['predictions']
>>> pred = preds[0]
>>> print(len(pred))
1000 # Because the classes is 1000
>>> print((-numpy.array(pred)).argsort()[:10]) # Get top-10 max
[667 457 906 610 834 796 841 652 620 465]
```

Detailed class list is listed here https://deeplearning.cms.waikato.ac.nz/user-guide/class-maps/IMAGENET/. From the prediction, we can get the label:
```
667: mortarboard
457: bow tie, bow-tie, bowtie
906: Windsor tie
610: jersey, T-shirt, tee shirt
834: suit, suit of clothes
796: ski mask
841: sweatshirt
652: military uniform
620: laptop, laptop computer
465: bulletproof vest
```

We have deployed the ResNet50, now will deploy another model, it's the ResNet101 model as a canary release. As in the case of the ResNet50 model, ResNet101 will be deployed as a Kubernetes Deployment annotated with the `app` label set to `image-classifier`. Recall that the `image-classifier` Kubernetes service is configured to load balance between pods that contain the `app` label set to this value and that the Istio virtual service is configured to forward all the traffic from the Istio Ingress gateway to the `image-classifier` service.

If you deployed ResNet101 without any changes to the Istio virtual service the incoming traffic would be load balanced across pods from both deployments using a `round-robin` strategy. To have a better control over which requests go to which deployment you need to configure a `destination rule` and modify the virtual service.

In this case, the destination rule configures two different subsets of the `image-classifier` service using the version label as a selector, in order to differentiate between ResNet50 and ResNet101 deployments:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: image-classifier
  namespace: tf-serving
spec:
  host: image-classifier
  subsets:
  - name: resnet101
    labels:
      version: resnet101
  - name: resnet50
    labels:
      version: resnet50
```

To create the destination rule:

```sh
$ kubectl apply -f destinationrule.yaml
destinationrule.networking.istio.io/image-classifier created
```

Recall that the ResNet50 deployment is annotated with two labels: app: image-classifier and version: resnet50. The ResNet101 deployment is also annotated with the same labels. The value of the app label is the same but the value of the version label is different:

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
        ports:
        - name: http
          containerPort: 8501
          protocol: TCP
        - name: grpc
          containerPort: 8500
          protocol: TCP
        volumeMounts:
        - name: model
          mountPath: /models/resnet101
      volumes:
      - name: model
        hostPath: 
          path: /home/hoang/Downloads/resnet101
```

The final step is to reconfigure the virtual service to use the destination rule.

You will start by modifying the virtual service to route all requests (100%) from the Ingress gateway to the resnet50 service subset:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: image-classifier
  namespace: tf-serving
spec:
  hosts:
  - "*"
  gateways:
  - image-classifier-gateway
  http:
  - route:
    - destination:
        host: image-classifier
        subset: resnet50
        port:
          number: 8501
      weight: 100
    - destination:
        host: image-classifier
        subset: resnet101
        port:
          number: 8501
      weight: 0
```

To apply the changes:

```sh
$ kubectl apply -f virtualservice-weight-100.yaml
virtualservice.networking.istio.io/image-classifier configured
```

Now deploy the ResNet101 model using the same process as for the ResNet50 model. Refer back to the steps above to the `kubectl` commands for applying updates to the configmaps and deployment configurations.

But we need to download the ResNet101 pretrained model using python code:
```python
>>> import tensorflow as tf

>>> print(tf.__version__)
2.6.2

>>> model = tf.keras.applications.resnet.ResNet101()
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet101_weights_tf_dim_ordering_tf_kernels.h5
179650560/179648224 [==============================] - 26s 0us/step

>>> model.save('/home/hoang/Downloads/resnet101/1') # 1 is version
INFO:tensorflow:Assets written to: /home/hoang/Downloads/resnet101/1/assets
```

Apply the manifest:

```sh
$ kubectl apply -f configmap-resnet101.yaml
configmap/resnet101-configs created

$ kubectl apply -f deployment-resnet101.yaml 
deployment.apps/image-classifier-resnet101 created

$ kubectl get deployments.apps -n tf-serving 
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
image-classifier-resnet101   1/1     1            1           41s
image-classifier-resnet50    1/1     1            1           51s
```

At this point the ResNet101 deployment is ready but the virtual service is configured to route all requests to ResNet50.

Verify this by sending a few prediction requests:

```python
>>> import requests, json, numpy
>>> pred = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                         json=json.load(open("request-body.json"))).json()['predictions'][0]
>>> print((-numpy.array(pred)).argsort()[:10])
[667 457 906 610 834 796 841 652 620 465]
```

All requests return the same result.

You will now reconfigure the Istio virtual service to split the traffic between the ResNet50 and ResNet101 models using weighted load balancing - 70% requests will go to ResNet50 and 30% to ResNet101.

The manifest for the new configuration is in the `virtualservice-weight-70.yaml` file:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: image-classifier
  namespace: tf-serving
spec:
  hosts:
  - "*"
  gateways:
  - image-classifier-gateway
  http:
  - route:
    - destination:
        host: image-classifier
        subset: resnet50
        port:
          number: 8501
      weight: 70
    - destination:
        host: image-classifier
        subset: resnet101
        port:
          number: 8501
      weight: 30
```

To apply the manifest:

```sh
$ kubectl apply -f virtualservice-weight-70.yaml
virtualservice.networking.istio.io/image-classifier configured
```

Send a few more requests - more than 10:

```python
>>> import requests, json, numpy

>>> pred = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                         json=json.load(open("request-body.json"))).json()['predictions'][0]
>>> print((-numpy.array(pred)).argsort()[:10])
[667 457 906 610 834 796 841 652 620 465]

>>> pred = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                         json=json.load(open("request-body.json"))).json()['predictions'][0]
>>> print((-numpy.array(pred)).argsort()[:10])
[906 667 834 400 457 652 451 465 841 917]
```

Notice that responses are now different.

As an optional task, you will reconfigure the virtual service to route traffic to the canary deployment based on request headers. This approach allows a variety of scenarios, including routing requests from a specific group of users to the canary release. Assume that the request from the canary users will carry a custom header user-group. If this header is set to canary the requests will be routed to ResNet101.

The `virtualservice-focused-routing.yaml` manifest defines this configuration:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: image-classifier
  namespace: tf-serving
spec:
  hosts:
  - "*"
  gateways:
  - image-classifier-gateway
  http:
  - match:
    - headers:
        user-group:
          exact: canary
    route:
      - destination:
          host: image-classifier
          subset: resnet101
          port:
            number: 8501
  - route:
    - destination:
        host: image-classifier
        subset: resnet50
        port:
          number: 8501
```

The match field defines a matching pattern and the route that is used for the requests with the matching header.

Reconfigure the virtual service:

```sh
$ kubectl apply -f virtualservice-focused-routing.yaml
virtualservice.networking.istio.io/image-classifier configured
```

Send a few requests without the `user-group` header:
```python
>>> import requests, json, numpy
>>> pred = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                         json=json.load(open("request-body.json"))).json()['predictions'][0]
>>> print((-numpy.array(pred)).argsort()[:10])
[667 457 906 610 834 796 841 652 620 465]
```

Notice that all of the responses are coming from the ResNet50 model.

Now, send a few requests with the `user-group` header set to `canary`:

```python
>>> import requests, json, numpy
>>> pred = requests.post(url="http://10.110.24.130:80/v1/models/image_classifier/versions/1:predict",
                         json=json.load(open("request-body.json")),
                         headers={"user-group": "canary"}).json()['predictions'][0]
>>> print((-numpy.array(pred)).argsort()[:10])
[906 667 834 400 457 652 451 465 841 917]
```

All of the responses are now sent by the ResNet101 model.

This deployment configuration can be used for A/B testing as you can easily monitor the performance of the canary model on a specific user group.

### Congratulations