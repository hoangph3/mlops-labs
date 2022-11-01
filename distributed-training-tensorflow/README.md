### Distributed training with TensorFlow on Kubernetes
Suppose we have already with minikube cluster look like that below:
```sh
$ minikube profile list
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
| Profile  | VM Driver | Runtime |     IP      | Port | Version | Status  | Nodes | Active |
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
| minikube | none      | docker  | 192.168.0.5 | 8443 | v1.24.3 | Running |     1 | *      |
|----------|-----------|---------|-------------|------|---------|---------|-------|--------|
```
If you aren't ready yet, following the instruction: https://github.com/hoangph3/devops-tutorial/tree/main/kubernetes/components/gpus

Create the `kubeflow` namespace:
```sh
$ kubectl create namespace kubeflow
namespace/kubeflow created
```

Install kubeflow training-operator:
```sh
$ kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone?ref=v1.5.0"
```

Verify installation:
```sh
$ kubectl get pods -n kubeflow
NAME                                 READY   STATUS    RESTARTS   AGE
training-operator-748d5cdc48-gffhk   1/1     Running   0          80s
```

Build a training container:
```sh
$ docker build -t mnist-distributed-training:v0.0.1 .
```

Submit a training job:
```sh
$ kubectl apply -f tfjob.yaml
tfjob.kubeflow.org/multi-worker created
```

Monitor the job:
```sh
$ kubectl describe tfjobs.kubeflow.org multi-worker
...
Normal   SuccessfulCreatePod  2m24s     tfjob-controller  Created pod: multi-worker-worker-0
Normal   SuccessfulCreatePod  2m24s     tfjob-controller  Created pod: multi-worker-worker-1
Normal   SuccessfulCreatePod  2m24s     tfjob-controller  Created pod: multi-worker-worker-2

$ kubectl get pods
NAME                                READY   STATUS    RESTARTS      AGE
multi-worker-worker-0               1/1     Running   0             12s
multi-worker-worker-1               1/1     Running   0             12s
multi-worker-worker-2               1/1     Running   0             12s

$ kubectl logs -f multi-worker-worker-0
Epoch 1/10
100/100 [==============================] - 19s 84ms/step - loss: 2.3002 - accuracy: 0.1213
Epoch 2/10
100/100 [==============================] - 8s 82ms/step - loss: 2.2512 - accuracy: 0.2613
Epoch 3/10
100/100 [==============================] - 8s 83ms/step - loss: 2.1932 - accuracy: 0.4032
Epoch 4/10
100/100 [==============================] - 8s 83ms/step - loss: 2.1053 - accuracy: 0.5168
Epoch 5/10
100/100 [==============================] - 9s 95ms/step - loss: 1.9883 - accuracy: 0.5827
Epoch 6/10
100/100 [==============================] - 9s 90ms/step - loss: 1.8277 - accuracy: 0.6753
Epoch 7/10
100/100 [==============================] - 9s 90ms/step - loss: 1.6206 - accuracy: 0.7193
Epoch 8/10
100/100 [==============================] - 9s 93ms/step - loss: 1.4133 - accuracy: 0.7405
Epoch 9/10
100/100 [==============================] - 9s 85ms/step - loss: 1.1952 - accuracy: 0.7876
Epoch 10/10
100/100 [==============================] - 12s 121ms/step - loss: 1.0255 - accuracy: 0.7938

$ kubectl logs -f multi-worker-worker-1
Epoch 1/10
100/100 [==============================] - 19s 87ms/step - loss: 2.2840 - accuracy: 0.1466
Epoch 2/10
100/100 [==============================] - 9s 85ms/step - loss: 2.1953 - accuracy: 0.3773
Epoch 3/10
100/100 [==============================] - 9s 90ms/step - loss: 2.0776 - accuracy: 0.5458
Epoch 4/10
100/100 [==============================] - 9s 89ms/step - loss: 1.9279 - accuracy: 0.6505
Epoch 5/10
100/100 [==============================] - 9s 92ms/step - loss: 1.7265 - accuracy: 0.7306
Epoch 6/10
100/100 [==============================] - 9s 86ms/step - loss: 1.5023 - accuracy: 0.7515
Epoch 7/10
100/100 [==============================] - 9s 89ms/step - loss: 1.2802 - accuracy: 0.7727
Epoch 8/10
100/100 [==============================] - 9s 93ms/step - loss: 1.0960 - accuracy: 0.8052
Epoch 9/10
100/100 [==============================] - 8s 83ms/step - loss: 0.9224 - accuracy: 0.8259
Epoch 10/10
100/100 [==============================] - 6s 61ms/step - loss: 0.8297 - accuracy: 0.8219

$ kubectl logs -f multi-worker-worker-2
Epoch 1/10
100/100 [==============================] - 20s 85ms/step - loss: 2.3063 - accuracy: 0.0720
Epoch 2/10
100/100 [==============================] - 8s 83ms/step - loss: 2.2620 - accuracy: 0.1988
Epoch 3/10
100/100 [==============================] - 9s 89ms/step - loss: 2.2118 - accuracy: 0.2999
Epoch 4/10
100/100 [==============================] - 8s 84ms/step - loss: 2.1418 - accuracy: 0.4118
Epoch 5/10
100/100 [==============================] - 9s 89ms/step - loss: 2.0414 - accuracy: 0.5416
Epoch 6/10
100/100 [==============================] - 9s 95ms/step - loss: 1.9031 - accuracy: 0.6236
Epoch 7/10
100/100 [==============================] - 9s 93ms/step - loss: 1.7247 - accuracy: 0.7008
Epoch 8/10
100/100 [==============================] - 9s 95ms/step - loss: 1.5122 - accuracy: 0.7417
Epoch 9/10
100/100 [==============================] - 8s 84ms/step - loss: 1.2802 - accuracy: 0.7831
Epoch 10/10
100/100 [==============================] - 7s 67ms/step - loss: 1.1046 - accuracy: 0.7928
```

Check saved model directory:
```sh
$ ls -la /home/hoang/Downloads/mnist/saved_model_dir
total 112
drwxrwxr-x 4 hoang hoang  4096 Thg 9 27 00:55 .
drwxrwxr-x 4 hoang hoang  4096 Thg 9 27 00:41 ..
drwxr-xr-x 2 root  root   4096 Thg 9 27 00:49 assets
-rw-r--r-- 1 root  root  96091 Thg 9 27 00:55 saved_model.pb
drwxr-xr-x 2 root  root   4096 Thg 9 27 00:55 variables
```