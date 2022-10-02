## Prepare and Deploy a TensorFlow Model to Tensorflow Serving

In this lab, we will:

1. Downloading and running the ResNet module
2. Creating serving signatures for the module
3. Exporting the model as a `SavedModel`
4. Deploying the `SavedModel` to AI Platform Prediction
5. Validating the deployed model
6. Advanced model server configuration

We will export two trained Resnet model, consist of Resnet50 and Resnet101, then serve these.

### 1. Download pretrained model from TFHub:
```sh
$ wget https://storage.googleapis.com/tfhub-modules/google/imagenet/resnet_v2_50/classification/5.tar.gz
$ wget https://storage.googleapis.com/tfhub-modules/google/imagenet/resnet_v2_101/classification/5.tar.gz
```
Then extract into a folder, similarity following to:
```sh
$ tree /home/hoang/Downloads/resnet
/home/hoang/Downloads/resnet
├── 101
│   ├── saved_model.pb
│   └── variables
│       ├── variables.data-00000-of-00001
│       └── variables.index
└── 50
    ├── saved_model.pb
    └── variables
        ├── variables.data-00000-of-00001
        └── variables.index
4 directories, 6 files
```

Note that the directory `50`, same as `101` is the version of the model.

The expected input to most TF2.x image classification models, is a rank `4` tensor conforming to the following tensor specification: `tf.TensorSpec([None, height, width, 3], tf.float32)`.
More concretely, the expected image size is height x width = `224 x 224`. The color values for all channels are expected to be normalized to the [0, 1] range.

The output of the model is a batch of logits vectors. The indices into the logits are the num_classes = `1001` classes from the ImageNet dataset. The mapping from indices to class labels can be found in the labels file with class `0` for "background", followed by `1000` actual ImageNet classes.

We will now test the model on a couple of JPEG images.

Display sample images:
```python
>>> import utils
>>> IMAGES_FOLDER="images"
>>> image_list = utils.get_image_list(image_dir=IMAGES_FOLDER)
>>> utils.show_image(image_list)
(720, 498, 3)
(600, 512, 3)
```
We get two images and its shape but the images need to be preprocessed to conform to the format expected `(224, 224, 3)` by the ResNet model.

```python
>>> size = 224
>>> raw_images = tf.stack(image_list)
>>> preprocessed_images = utils.preprocess_image(raw_images, size)
>>> preprocessed_images.shape
TensorShape([2, 224, 224, 3])
```

Run inference:
```python
>>> model = tf.keras.models.load_model('/home/hoang/Downloads/resnet/101')
>>> predictions = model(preprocessed_images)
>>> predictions
<tf.Tensor: shape=(2, 1001), dtype=float32, numpy=
array([[ 0.27374715, -1.2126322 , -0.85858756, ..., -1.8846453 ,
         0.25237346,  1.8259864 ],
       [ 0.28163522,  0.61459076, -0.00311601, ..., -0.5948272 ,
        -0.05215326, -0.11519516]], dtype=float32)>
```

The model returns a batch of arrays with logits. This is not a very user friendly output so we will convert it to the list of ImageNet class labels.

```python
>>> import numpy as np
>>> imagenet_labels = np.array(open("labels/ImageNetLabels.txt").read().splitlines())
>>> imagenet_labels
array(['background', 'tench', 'goldfish', ..., 'bolete', 'ear',
       'toilet tissue'], dtype='<U30')
```

### 2. Create Serving Signatures:

The inputs and outputs of the model as used during model training may not be optimal for serving. For example, in a typical training pipeline, feature engineering is performed as a separate step preceding model training and hyperparameter tuning. When serving the model, it may be more optimal to embed the feature engineering logic into the serving interface rather than require a client application to preprocess data.

The ResNet model from TFHub is optimized for recomposition and fine-tuning. Since there are no serving signatures in the model's metadata, it cannot be served with TF Serving as is.

To make it servable, we need to add a serving signature(s) describing the inference method(s) of the model. We will add two signatures:
- `The default signature`: this will expose the default predict method of the ResNet model.
- `Prep/post-processing signature`: since the expected inputs to this interface require a relatively complex image preprocessing to be performed by a client, we will also expose an alternative signature that embeds the preprocessing and postprocessing logic and accepts raw unprocessed images and returns the list of ranked class labels and associated label probabilities.

The signatures are created by defining a custom module class derived from the `tf.Module` base class. The custom module will be exported as `SavedModel` that includes the original model, the preprocessing logic, and two serving signatures.

Test the custom serving module:
```python
>>> serving_module = utils.ServingModule(model, size, imagenet_labels)
>>> predictions = serving_module.predict_labels(raw_images)
>>> predictions
{'labels': <tf.Tensor: shape=(2, 5), dtype=string, numpy=
array([[b'Egyptian cat', b'tiger cat', b'tabby', b'lynx', b'Siamese cat'],
       [b'military uniform', b'suit', b'Windsor tie', b'pickelhaube',
        b'bow tie']], dtype=object)>, 'probabilities': <tf.Tensor: shape=(2, 5), dtype=float32, numpy=
array([[8.2705331e-01, 1.3128258e-01, 4.1055005e-02, 5.7081261e-04,
        1.8924713e-05],
       [9.4001341e-01, 4.8532788e-02, 6.4066364e-03, 2.0129983e-03,
        6.0433790e-04]], dtype=float32)>}
```

In this case, my custom serving module only get top-5 labels that have highest probabilities.

### 3. Save the custom serving module as `SavedModel`
```python
>>> model_path = "/home/hoang/Downloads/resnet_serving/101"
>>> default_signature = serving_module.__call__.get_concrete_function()
>>> preprocess_signature = serving_module.predict_labels.get_concrete_function()
>>> signatures = {'serving_default': default_signature,
                  'serving_preprocess': preprocess_signature}
>>> tf.saved_model.save(serving_module, model_path, signatures=signatures)
INFO:tensorflow:Assets written to: /home/hoang/Downloads/resnet_serving/101/assets
```

Verify the Resnet model serving:
```sh
$ saved_model_cli show --dir "${model_path}" --tag_set serve --all
...
MetaGraphDef with tag-set: 'serve' contains the following SignatureDefs:

signature_def['__saved_model_init_op']:
  The given SavedModel SignatureDef contains the following input(s):
  The given SavedModel SignatureDef contains the following output(s):
    outputs['__saved_model_init_op'] tensor_info:
        dtype: DT_INVALID
        shape: unknown_rank
        name: NoOp
  Method name is: 

signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['x'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 224, 224, 3)
        name: serving_default_x:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['output_0'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 1001)
        name: StatefulPartitionedCall:0
  Method name is: tensorflow/serving/predict

signature_def['serving_preprocess']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['raw_images'] tensor_info:
        dtype: DT_STRING
        shape: (-1)
        name: serving_preprocess_raw_images:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['labels'] tensor_info:
        dtype: DT_STRING
        shape: (-1, -1)
        name: StatefulPartitionedCall_1:0
    outputs['probabilities'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, -1)
        name: StatefulPartitionedCall_1:1
  Method name is: tensorflow/serving/predict

Defined Functions:
  Function Name: '__call__'
    Option #1
      Callable with:
        Argument #1
          x: TensorSpec(shape=(None, 224, 224, 3), dtype=tf.float32, name='x')

  Function Name: 'predict_labels'
    Option #1
      Callable with:
        Argument #1
          raw_images: TensorSpec(shape=(None,), dtype=tf.string, name='raw_images')
```

Test loading and executing the `SavedModel`:
```python
>>> model = tf.keras.models.load_model(model_path)
>>> model.predict_labels(raw_images)
{'probabilities': <tf.Tensor: shape=(2, 5), dtype=float32, numpy=
array([[8.2705331e-01, 1.3128258e-01, 4.1055005e-02, 5.7081261e-04,
        1.8924713e-05],
       [9.4001341e-01, 4.8532788e-02, 6.4066364e-03, 2.0129983e-03,
        6.0433790e-04]], dtype=float32)>, 'labels': <tf.Tensor: shape=(2, 5), dtype=string, numpy=
array([[b'Egyptian cat', b'tiger cat', b'tabby', b'lynx', b'Siamese cat'],
       [b'military uniform', b'suit', b'Windsor tie', b'pickelhaube',
        b'bow tie']], dtype=object)>}
```

We can absolutely do the same with the Resnet50 model. Finally we have the custom serving module for Resnet model with two version, `50` and `101`.

```sh
$ tree /home/hoang/Downloads/resnet_serving
├── 101
│   ├── assets
│   ├── saved_model.pb
│   └── variables
│       ├── variables.data-00000-of-00001
│       └── variables.index
└── 50
    ├── assets
    ├── saved_model.pb
    └── variables
        ├── variables.data-00000-of-00001
        └── variables.index
6 directories, 6 files
```

### 4. Deploying the `SavedModel`

Now we will serving multiple versions of the Resnet model, by write model config `models.config` file.
```conf
model_config_list: {
  config: {
    name: "resnet",
    base_path: "/models/resnet"
    model_platform: "tensorflow",
    model_version_policy: {
      all: {}
    }
  }
}
```

Write the `docker-compose.yaml` file:
```yaml
version: '3.2'
services:
  tf-serving:
    container_name: tf_serving
    image: tensorflow/serving:2.5.1
    ports:
      - "8501:8501"
      - "8500:8500"
    volumes:
      - "/home/hoang/Downloads/resnet_serving:/models/resnet"
      - "./models.config:/models/models.config"
    command:
      - '--model_config_file=/models/models.config'
      - '--model_config_file_poll_wait_seconds=60'
```

Deploying the model by `docker-compose` command:
```sh
$ docker-compose up -d
[+] Running 2/2
 ⠿ Network tensorflow-serving-configuration_default  Created            0.2s
 ⠿ Container tf_serving                              Started            1.2s

$ docker ps | grep tf_serving
e1f6a5ed1276   tensorflow/serving:2.5.1   "/usr/bin/tf_serving…"   About a minute ago   Up About a minute   0.0.0.0:8500-8501->8500-8501/tcp, :::8500-8501->8500-8501/tcp   tf_serving

$ docker logs -f tf_serving
...
2022-10-01 11:26:22.126759: I tensorflow_serving/servables/tensorflow/saved_model_warmup_util.cc:59] No warmup data file found at /models/resnet/50/assets.extra/tf_serving_warmup_requests
2022-10-01 11:26:23.183213: I tensorflow_serving/model_servers/server.cc:393] Running gRPC ModelServer at 0.0.0.0:8500 ...
[warn] getaddrinfo: address family for nodename not supported
2022-10-01 11:26:23.185253: I tensorflow_serving/model_servers/server.cc:414] Exporting HTTP/REST API at:localhost:8501 ...
[evhttp_server.cc : 245] NET_LOG: Entering the event loop ...
```

### 5. Validating the deployed model
```sh
$ curl -d @payloads/request-body.json -X POST http://localhost:8501/v1/models/resnet/versions/50:predict
{
    "predictions": [
        {
            "labels": ["military uniform", "pickelhaube", "suit", "Windsor tie", "bearskin"],
            "probabilities": [0.453408211, 0.209194973, 0.193582058, 0.0409308933, 0.0137334978]
        }
    ]
}
$ curl -d @payloads/request-body.json -X POST http://localhost:8501/v1/models/resnet/versions/101:predict
{
    "predictions": [
        {
            "probabilities": [0.940013, 0.0485330448, 0.00640664576, 0.0020130109, 0.000604341098],
            "labels": ["military uniform", "suit", "Windsor tie", "pickelhaube", "bow tie"]
        }
    ]
}
```

### 6. Advanced model server configuration

#### 6.1. SavedModel Warmup

As soon as you have just deployed the model without a warm up, you can see the response time look like that:
```sh
$ curl -d @payloads/request-body.json -X POST http://localhost:8501/v1/models/resnet/versions/50:predict -o /dev/null -s -w 'Total: %{time_total}s\n'
Total: 1,423064s
```

To enable model warmup, you will use user-provided PredictionLogs in `assets.extra/` directory. Fisrtly, generating the PredictionLogs from module `utils/warmup_serving.py` and save into a file:
```sh
$ python3 utils/warmup_serving.py
...
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.

$ tree /home/hoang/Downloads/resnet_serving
/home/hoang/Downloads/resnet_serving
├── 101
│   ├── assets
│   ├── assets.extra
│   │   └── tf_serving_warmup_requests
│   ├── saved_model.pb
│   └── variables
│       ├── variables.data-00000-of-00001
│       └── variables.index
└── 50
    ├── assets
    ├── assets.extra
    │   └── tf_serving_warmup_requests
    ├── saved_model.pb
    └── variables
        ├── variables.data-00000-of-00001
        └── variables.index
8 directories, 8 files
```

Now we will test the model serving with a warm up
```sh
# Re-create the container
$ docker-compose up -d
[+] Running 2/2
 ⠿ Network tensorflow-serving-configuration_default  Created            0.1s
 ⠿ Container tf_serving                              Started            0.8s

# Trace logs
$ docker logs -f tf_serving
...
2022-10-02 06:53:31.495273: I tensorflow_serving/servables/tensorflow/saved_model_warmup_util.cc:122] Finished reading warmup data for model at /models/resnet/50/assets.extra/tf_serving_warmup_requests. Number of warmup records read: 200. Elapsed time (microseconds): 45988765.

# Exec curl
curl -d @payloads/request-body.json -X POST http://localhost:8501/v1/models/resnet/versions/50:predict -o /dev/null -s -w 'Total: %{time_total}s\n'
Total: 0,129297s
```

It is easy to see that a Warmup helps the model to start up faster.

