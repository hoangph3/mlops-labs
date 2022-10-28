### Setup environments
[Link here!](/seldon-core/inference-graph/README.md/)

### Training a model
```sh
$ python3 train.py
*
optimization finished, #iter = 8
obj = -4.874554, rho = -0.126317
nSV = 11, nBSV = 8
*
optimization finished, #iter = 17
obj = -2.130718, rho = 0.064464
nSV = 8, nBSV = 2
*
optimization finished, #iter = 37
obj = -34.058808, rho = 0.107043
nSV = 47, nBSV = 45
Total nSV = 60
```

### Write a class wrapper that exposes the logic of your model
```python
import pickle
from sklearn import svm

class IrisClassifier:
    def __init__(self):
        self._model: svm.SVC = pickle.load(open("model.pkl", "rb"))

    def predict(self, X, features_names=None, meta=None):
        output = self._model.predict(X)
        return output
```

### Build image
```sh
$ docker build -t sklearn_iris_classifier:0.0.1 .
```

### Deploy the model
1. Create a namespace to run your model in:
```sh
$ kubectl create namespace seldon-model
namespace/seldon created
```

2. Create the manifest file `deploy-model.yaml`
```yaml
apiVersion: machinelearning.seldon.io/v1alpha2
kind: SeldonDeployment
metadata:
  name: iris-model
  namespace: seldon-model
spec:
  name: iris
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: sklearn_iris_classifier:0.0.1
    graph:
      name: classifier
    name: default
    replicas: 1
```

3. Deploy it to our Seldon Core Kubernetes Cluster:
```sh
$ kubectl apply -f deploy-model.yaml
seldondeployment.machinelearning.seldon.io/iris-model created

$ kubectl get pods -n seldon-model
NAME                                               READY   STATUS    RESTARTS   AGE
iris-model-default-0-classifier-64d68cbd8d-tj2r5   3/3     Running   0          38s
```

### Testing
```sh
$ export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

$ echo $INGRESS_HOST
10.106.254.233

$ curl -X POST -d @payload.json -H 'Content-Type: application/json' \
    http://$INGRESS_HOST/seldon/seldon-model/iris-model/api/v1.0/predictions | json_pp

{
   "data" : {
      "ndarray" : [
         2
      ],
      "names" : []
   },
   "meta" : {
      "requestPath" : {
         "classifier" : "sklearn_iris_classifier:0.0.1"
      }
   }
}
```
