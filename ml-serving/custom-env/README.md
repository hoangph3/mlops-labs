# Custom Conda environments in MLServer

It's not unusual that model runtimes require extra dependencies that are not direct dependencies of MLServer. This is the case when we want to use `custom runtimes`.

In these cases, since these dependencies (or dependency versions) are not known in advance by MLServer, they **won't be included in the default `seldonio/mlserver` Docker image**.
To cover these cases, the **`seldonio/mlserver` Docker image allows you to load custom environments** before starting the server itself.

This example will walk you through how to create and save an custom environment, so that it can be loaded in MLServer without any extra change to the `seldonio/mlserver` Docker image. 

## Define our environment

For this example, we will create a custom environment to serve a model trained with Faiss. 
The first step will be define this environment, using a [`environment.yml`](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#create-env-file-manually). 

Note that these environments can also be created on the fly as we go, and then serialised later.


```python
%%writefile environment.yml

name: faiss
channels:
    - conda-forge
dependencies:
    - python == 3.8
    - faiss-cpu
    - pip
```

### Train model in our custom environment

The first step will be to create and activate an environment which reflects what's outlined in our `environment.yml` file.

> **NOTE:** If you are running this from a Jupyter Notebook, you will need to restart your Jupyter instance so that it runs from this environment.


```bash
bash create_env.sh
```

### Serialise our custom environment

Lastly, we will need to serialise our environment in the format expected by MLServer.
To do that, we will use a tool called [`conda-pack`](https://conda.github.io/conda-pack/).

This tool, will save a portable version of our environment as a `.tar.gz` file, also known as _tarball_.


```bash
bash export_env.sh
```

## Serving 

Now that we have defined our environment (and we've got a sample artifact trained in that environment), we can move to serving our model.

To do that, we will first need to select the right runtime through a `model-settings.json` config file.


```python
%%writefile model-settings.json
{
    "name": "mnist",
    "implementation": "serve_model.Mnist",
    "parameters": {
        "environment_tarball": "/mnt/models/faiss.tar.gz"
    }
}
```

We can then spin up our model, using our custom environment, leveraging MLServer's Docker image.
Keep in mind that **you will need Docker installed in your machine to run this example**.

Our Docker command will need to take into account the following points:

- Mount the example's folder as a volume so that it can be accessed from within the container.
- Let MLServer know that our custom environment's tarball can be found as `old-sklearn.tar.gz`.
- Expose port `9080` so that we can send requests from the outside. 

From the command line, this can be done using Docker's CLI as:

```bash
bash run_docker.sh
```

```
2023-07-29 07:32:12,619 [mlserver] INFO - Extracting environment tarball from /mnt/models/faiss.tar.gz...
2023-07-29 07:32:16,004 [mlserver.parallel] DEBUG - Starting response processing loop...
2023-07-29 07:32:17.343874: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2023-07-29 07:32:17.395480: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2023-07-29 07:32:17.396004: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2023-07-29 07:32:18.412235: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
Model: "sequential"
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 reshape (Reshape)           (None, 28, 28, 1)         0         
                                                                 
 conv2d (Conv2D)             (None, 26, 26, 32)        320       
                                                                 
 flatten (Flatten)           (None, 21632)             0         
                                                                 
 dense (Dense)               (None, 128)               2769024   
                                                                 
 dense_1 (Dense)             (None, 10)                1290      
                                                                 
=================================================================
Total params: 2770634 (10.57 MB)
Trainable params: 2770634 (10.57 MB)
Non-trainable params: 0 (0.00 Byte)
_________________________________________________________________
Load faiss: 1.7.4
2023-07-29 07:32:19,779 [mlserver] INFO - Loaded model 'mnist' succesfully.
2023-07-29 07:32:19,781 [mlserver] INFO - Loaded model 'mnist' succesfully.
```

Note that we need to keep the server running in the background while we send requests.
Therefore, it's best to run this command on a separate terminal session.

### Send test inference request

We now have our model being served by `mlserver`.
To make sure that everything is working as expected, let's send a request from our test set.

For that, we can use the Python types that `mlserver` provides out of box, or we can build our request manually.


```python
python3 test.py
```
