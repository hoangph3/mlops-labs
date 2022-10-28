# Train Various Models on MNIST using kubeflow and seldon-core

1. Install kubeflow training-operator
```sh
$ kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone?ref=v1.5.0"
```

2. Build training and serving components
```sh
$ python3 build_component.py
```

3. Create a persistent volume to save model file
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: "nfs-1"
  namespace: seldon-model
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 4Gi
```
```sh
$ kubectl apply -f pvc.yml
persistentvolumeclaim/nfs-1 created
```

3. Training tensorflow mnist model by the manifest file:
```sh
$ kubectl apply -f tf_mnist_training.yml 
tfjob.kubeflow.org/tf-mnist-training created

$ kubectl get pods -n seldon-model tf-mnist-training-worker-0 
NAME                         READY   STATUS    RESTARTS   AGE
tf-mnist-training-worker-0   2/2     Running   0          43s

$ kubectl logs -f -n seldon-model tf-mnist-training-worker-0
Model: "sequential"
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
dense (Dense)                (None, 128)               100480    
_________________________________________________________________
dense_1 (Dense)              (None, 64)                8256      
_________________________________________________________________
dense_2 (Dense)              (None, 10)                650       
=================================================================
Total params: 109,386
Trainable params: 109,386
Non-trainable params: 0
_________________________________________________________________
Epoch 1/20
938/938 [==============================] - 8s 4ms/step - loss: 2.2312 - accuracy: 0.1851 - val_loss: 1.8747 - val_accuracy: 0.5213
2022-10-28 14:48:01.857621: W tensorflow/core/framework/cpu_allocator_impl.cc:80] Allocation of 47040000 exceeds 10% of free system memory.
Epoch 2/20
938/938 [==============================] - 3s 3ms/step - loss: 1.7639 - accuracy: 0.5803 - val_loss: 1.3615 - val_accuracy: 0.7254
2022-10-28 14:48:04.905285: W tensorflow/core/framework/cpu_allocator_impl.cc:80] Allocation of 47040000 exceeds 10% of free system memory.
Epoch 3/20
938/938 [==============================] - 4s 4ms/step - loss: 1.2764 - accuracy: 0.7416 - val_loss: 0.9752 - val_accuracy: 0.7975
Epoch 4/20
938/938 [==============================] - 4s 4ms/step - loss: 0.9448 - accuracy: 0.7993 - val_loss: 0.7602 - val_accuracy: 0.8338
Epoch 5/20
938/938 [==============================] - 3s 3ms/step - loss: 0.7512 - accuracy: 0.8294 - val_loss: 0.6379 - val_accuracy: 0.8522
Epoch 6/20
938/938 [==============================] - 3s 3ms/step - loss: 0.6378 - accuracy: 0.8487 - val_loss: 0.5612 - val_accuracy: 0.8637
Epoch 7/20
938/938 [==============================] - 4s 4ms/step - loss: 0.5654 - accuracy: 0.8591 - val_loss: 0.5081 - val_accuracy: 0.8730
Epoch 8/20
938/938 [==============================] - 3s 3ms/step - loss: 0.5128 - accuracy: 0.8704 - val_loss: 0.4698 - val_accuracy: 0.8798
Epoch 9/20
938/938 [==============================] - 3s 4ms/step - loss: 0.4876 - accuracy: 0.8723 - val_loss: 0.4410 - val_accuracy: 0.8855
Epoch 10/20
938/938 [==============================] - 4s 4ms/step - loss: 0.4569 - accuracy: 0.8768 - val_loss: 0.4181 - val_accuracy: 0.8905
Epoch 11/20
938/938 [==============================] - 3s 3ms/step - loss: 0.4340 - accuracy: 0.8811 - val_loss: 0.4004 - val_accuracy: 0.8940
Epoch 12/20
938/938 [==============================] - 3s 4ms/step - loss: 0.4115 - accuracy: 0.8867 - val_loss: 0.3850 - val_accuracy: 0.8962
Epoch 13/20
938/938 [==============================] - 4s 4ms/step - loss: 0.3953 - accuracy: 0.8902 - val_loss: 0.3724 - val_accuracy: 0.8987
Epoch 14/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3857 - accuracy: 0.8935 - val_loss: 0.3619 - val_accuracy: 0.9010
Epoch 15/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3741 - accuracy: 0.8951 - val_loss: 0.3525 - val_accuracy: 0.9037
Epoch 16/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3680 - accuracy: 0.8965 - val_loss: 0.3442 - val_accuracy: 0.9049
Epoch 17/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3569 - accuracy: 0.8998 - val_loss: 0.3371 - val_accuracy: 0.9069
Epoch 18/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3552 - accuracy: 0.9004 - val_loss: 0.3306 - val_accuracy: 0.9078
Epoch 19/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3435 - accuracy: 0.9037 - val_loss: 0.3244 - val_accuracy: 0.9085
Epoch 20/20
938/938 [==============================] - 3s 3ms/step - loss: 0.3415 - accuracy: 0.9042 - val_loss: 0.3188 - val_accuracy: 0.9108
INFO:root:Saving the trained model to: /models/saved_model_dir
2022-10-28 14:49:04.714874: W tensorflow/python/util/util.cc:348] Sets are not currently considered sequences, but this may change in the future, so consider avoiding using them.
INFO:tensorflow:Assets written to: /models/saved_model_dir/assets
INFO:tensorflow:Assets written to: /models/saved_model_dir/assets
```

4. Training sklearn mnist model by the manifest file:
```sh
$ kubectl apply -f components_spec/sk_mnist_training.yml 
job.batch/sk-mnist-training created

$ kubectl get pods -n seldon-model 
NAME                      READY   STATUS    RESTARTS   AGE
sk-mnist-training-5xpkj   2/2     Running   0          21s

$ kubectl logs -f -n seldon-model sk-mnist-training-knrzv 
Train report RandomForestClassifier(n_estimators=15):
              precision    recall  f1-score   support

           0       1.00      1.00      1.00      5923
           1       1.00      1.00      1.00      6742
           2       1.00      1.00      1.00      5958
           3       1.00      1.00      1.00      6131
           4       1.00      1.00      1.00      5842
           5       1.00      1.00      1.00      5421
           6       1.00      1.00      1.00      5918
           7       1.00      1.00      1.00      6265
           8       1.00      1.00      1.00      5851
           9       1.00      1.00      1.00      5949

    accuracy                           1.00     60000
   macro avg       1.00      1.00      1.00     60000
weighted avg       1.00      1.00      1.00     60000


Train confusion matrix:
[[5923    0    0    0    0    0    0    0    0    0]
 [   0 6741    1    0    0    0    0    0    0    0]
 [   1    0 5955    0    0    0    0    1    1    0]
 [   0    0    1 6129    0    0    0    0    1    0]
 [   0    0    0    0 5841    0    0    0    0    1]
 [   0    0    0    1    0 5420    0    0    0    0]
 [   1    0    0    0    0    0 5917    0    0    0]
 [   0    0    1    0    0    0    0 6264    0    0]
 [   0    0    0    0    0    0    0    0 5851    0]
 [   1    0    0    1    1    1    0    1    0 5944]]
Test report RandomForestClassifier(n_estimators=15):
              precision    recall  f1-score   support

           0       0.97      0.99      0.98       980
           1       0.98      0.99      0.99      1135
           2       0.94      0.95      0.95      1032
           3       0.95      0.95      0.95      1010
           4       0.96      0.96      0.96       982
           5       0.95      0.93      0.94       892
           6       0.97      0.97      0.97       958
           7       0.96      0.94      0.95      1028
           8       0.93      0.94      0.94       974
           9       0.96      0.93      0.94      1009

    accuracy                           0.96     10000
   macro avg       0.96      0.96      0.96     10000
weighted avg       0.96      0.96      0.96     10000


Test confusion matrix:
[[ 969    0    0    2    0    3    2    1    3    0]
 [   0 1123    4    2    0    2    1    0    2    1]
 [   7    0  983    5    4    1    5   11   16    0]
 [   0    0   14  956    0   15    1   12   10    2]
 [   3    0    2    0  938    0    9    2    7   21]
 [   6    0    5   17    4  833    7    2   15    3]
 [   8    3    4    0    3    6  928    0    6    0]
 [   2   10   23    5    5    1    0  971    3    8]
 [   2    0   11   13    3   10    6    3  917    9]
 [   7    7    1   10   19   10    0    5    7  943]]
Save model to /models/sk_mnist.pkl
```

# Deploying Various MNIST Models on Kubernetes

1. Serving tensorflow model
```sh
$ kubectl apply -f tf_mnist_serving.yml
seldondeployment.machinelearning.seldon.io/tf-mnist created

$ kubectl get pods -n seldon-model tf-mnist-tf-mnist-0-tf-mnist-5b898df979-2fgkd 
NAME                                            READY   STATUS    RESTARTS   AGE
tf-mnist-tf-mnist-0-tf-mnist-5b898df979-2fgkd   3/3     Running   0          30s

$ export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

$ echo $INGRESS_HOST
10.106.254.233

$ curl -X POST -d @payload.json -H 'Content-Type: application/json' \
    http://$INGRESS_HOST/seldon/seldon-model/tf-mnist/api/v1.0/predictions | json_pp
{
   "data" : {
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
      ],
      "ndarray" : [
         [
            4.48017120361328,
            -9.0218448638916,
            4.17771196365356,
            -5.54879522323608,
            1.39498293399811,
            1.59465968608856,
            11.3906955718994,
            -5.56072759628296,
            -1.04759287834167,
            -2.57119679450989
         ]
      ]
   },
   "meta" : {
      "requestPath" : {
         "tf-mnist" : "hoangph3/tf_mnist_serving:v0.0.1"
      }
   }
}
```

2. Serving sklearn model
```sh
$ kubectl apply -f components_spec/sk_mnist_serving.yml 
seldondeployment.machinelearning.seldon.io/sk-mnist created

$ kubectl get pods -n seldon-model sk-mnist-sk-mnist-0-sk-mnist-686dd8f7-9h6wp 
NAME                                          READY   STATUS    RESTARTS   AGE
sk-mnist-sk-mnist-0-sk-mnist-686dd8f7-9h6wp   3/3     Running   0          54s

$ curl -X POST -d @payload.json -H 'Content-Type: application/json' \
    http://$INGRESS_HOST/seldon/seldon-model/sk-mnist/api/v1.0/predictions | json_pp
{
   "meta" : {
      "requestPath" : {
         "sk-mnist" : "hoangph3/sk_mnist_serving:v0.0.1"
      }
   },
   "data" : {
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
      ],
      "ndarray" : [
         [
            0,
            0.0666666666666667,
            0.2,
            0,
            0.2,
            0.2,
            0.133333333333333,
            0.0666666666666667,
            0.0666666666666667,
            0.0666666666666667
         ]
      ]
   }
}
```