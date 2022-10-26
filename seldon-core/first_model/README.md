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
class Model:
    def __init__(self):
        self._model = pickle.loads(open("model.pkl", "rb") )

    def predict(self, X):
        output = self._model(X)
        return output
```

### Build image
```sh
$ docker build -t sklearn_iris:0.1 .
Sending build context to Docker daemon  11.26kB
Step 1/5 : FROM python:3.8-slim-buster
 ---> 60abb4f18941
Step 2/5 : WORKDIR /app
 ---> Using cache
 ---> 6a32cb03c453
Step 3/5 : COPY model.pkl .
 ---> 670fcf306cd4
Step 4/5 : COPY Model.py .
 ---> 9447eccb286a
Step 5/5 : CMD ["python", "Model.py"]
 ---> Running in 7c293506409b
Removing intermediate container 7c293506409b
 ---> 763eaf73d0c5
Successfully built 763eaf73d0c5
Successfully tagged sklearn_iris:0.
```

### Deploy the model
Create a namespace to run your model in:
```sh
$ kubectl create namespace seldon
namespace/seldon created
```

Create the manifest file `deploy-model.yaml`
```yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: iris-model
  namespace: seldon
spec:
  name: iris
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: sklearn_iris:0.1
    graph:
      name: classifier
    name: default
    replicas: 1
```

Deploy it to our Seldon Core Kubernetes Cluster:
```sh
$ kubectl apply -f deploy-model.yaml
seldondeployment.machinelearning.seldon.io/iris-model created
```