## Prepare and Deploy a TensorFlow Model to Tensorflow Serving

In this lab, we will:

1. Downloading and running the ResNet module
2. Creating serving signatures for the module
3. Exporting the model as a `SavedModel`
4. Deploying the `SavedModel` to AI Platform Prediction
5. Validating the deployed model

We will export two trained Resnet model, consist of Resnet50 and Resnet101, then serve these.

### 1. Download pretrained model by python code:
```python
>>> import tensorflow as tf

>>> print(tf.__version__)
2.6.2

>>> model = tf.keras.applications.resnet50.ResNet50()
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet50_weights_tf_dim_ordering_tf_kernels.h5
102973440/102967424 [==============================] - 32s 0us/step

>>> model.save('/home/hoang/Downloads/resnet/50') # 50 is version
INFO:tensorflow:Assets written to: /home/hoang/Downloads/resnet/50/assets

>>> model = tf.keras.applications.resnet.ResNet101()
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet101_weights_tf_dim_ordering_tf_kernels.h5
179650560/179648224 [==============================] - 26s 0us/step

>>> model.save('/home/hoang/Downloads/resnet/101') # 101 is version
INFO:tensorflow:Assets written to: /home/hoang/Downloads/resnet/101/assets
```

Verify the directory have saved model:
```sh
$ tree /home/hoang/Downloads/resnet
/home/hoang/Downloads/resnet/
├── 101
│   ├── assets
│   ├── keras_metadata.pb
│   ├── saved_model.pb
│   └── variables
│       ├── variables.data-00000-of-00001
│       └── variables.index
└── 50
    ├── assets
    ├── keras_metadata.pb
    ├── saved_model.pb
    └── variables
        ├── variables.data-00000-of-00001
        └── variables.index
6 directories, 8 files
```

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
tf.Tensor(
[[1.47234459e-04 2.66434450e-04 4.65371741e-05 ... 1.19409679e-05
  1.21960125e-04 6.29067828e-04]
 [1.12211841e-04 2.68791919e-04 7.37712617e-05 ... 1.11050695e-05
  1.50396168e-04 1.09615386e-03]], shape=(2, 1000), dtype=float32)
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
```