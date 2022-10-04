### Building Kubeflow Components 

Pipeline components are self-contained sets of code that perform one step in your ML workflow, such as preprocessing data or training a model. To create a component, you must build the component's implementation and define the component specification. This document describes the concepts required to build components, and demonstrates how to get started building components.

#### 1. Install the Kubeflow Pipelines SDK:
```sh
$ export PIPELINE_VERSION=1.8.5

$ pip3 install kfp==$PIPELINE_VERSION

$ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION&timeout=300"

$ kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io

$ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"

$ kubectl get pods -n kubeflow
NAME                                               READY   STATUS    RESTARTS      AGE
cache-deployer-deployment-679cb5c746-4lrsj         1/1     Running   0             36s
cache-server-864c559d7f-ql5cb                      1/1     Running   0             36s
metadata-envoy-deployment-7c8fc4dc6c-w9qvz         1/1     Running   0             35s
metadata-grpc-deployment-5c8599b99c-h6qn9          1/1     Running   2 (29s ago)   35s
metadata-writer-664d5b498d-zc9zg                   1/1     Running   0             35s
minio-6d6d45469f-59p4p                             1/1     Running   0             35s
ml-pipeline-7b4b88c975-4cnth                       1/1     Running   0             35s
ml-pipeline-persistenceagent-77bdd854b8-mszrn      1/1     Running   0             35s
ml-pipeline-scheduledworkflow-7bbb6c9dc9-nxdsj     1/1     Running   0             35s
ml-pipeline-ui-b77595fcf-lmj8j                     1/1     Running   0             35s
ml-pipeline-viewer-crd-7c87784fcf-2rpx9            1/1     Running   0             35s
ml-pipeline-visualizationserver-754c5dd4dd-ltn7f   1/1     Running   0             34s
mysql-55778745b6-lddcp                             1/1     Running   0             34s
workflow-controller-b7f95d6c6-d4lt2                1/1     Running   0             34s
```

When everything is ready, you can run the following command to access the `ml-pipeline-ui` service.

```sh
$ kubectl get svc -n kubeflow ml-pipeline-ui
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
ml-pipeline-ui   ClusterIP   10.99.209.141   <none>        80/TCP    76s

$ kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
Forwarding from 127.0.0.1:8080 -> 3000
Forwarding from [::1]:8080 -> 3000
```

You can then open your browser and go to http://localhost:8080 to see the user interface.

#### 2. Building components and pipeline
```sh
$ python3 build_component.py
$ python3 build_pipeline.py
```

#### 4. Run pipeline

- Upload pipeline
- Create new experiment
- Run pipeline in the experiment