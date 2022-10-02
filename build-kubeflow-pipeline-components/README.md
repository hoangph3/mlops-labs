### Building Kubeflow Components 

Pipeline components are self-contained sets of code that perform one step in your ML workflow, such as preprocessing data or training a model. To create a component, you must build the component's implementation and define the component specification. This document describes the concepts required to build components, and demonstrates how to get started building components.

1. Install the Kubeflow Pipelines SDK:
```sh
$ export PIPELINE_VERSION=1.8.5

$ pip3 install kfp==$PIPELINE_VERSION

$ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION&timeout=300"

$ kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io

$ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"

$ kubectl get pods -n kubeflow
NAME                                               READY   STATUS    RESTARTS        AGE
cache-deployer-deployment-679cb5c746-4g975         1/1     Running   0               19m
cache-server-864c559d7f-rwwx7                      1/1     Running   0               19m
metadata-envoy-deployment-7c8fc4dc6c-7jp7l         1/1     Running   0               19m
metadata-grpc-deployment-5c8599b99c-dr2gs          1/1     Running   7 (12m ago)     19m
metadata-writer-664d5b498d-9p8hk                   1/1     Running   2 (7m19s ago)   19m
minio-6d6d45469f-xvw2f                             1/1     Running   0               19m
ml-pipeline-7b4b88c975-xxr87                       1/1     Running   1 (9m39s ago)   19m
ml-pipeline-persistenceagent-77bdd854b8-rtn76      1/1     Running   2 (9m3s ago)    19m
ml-pipeline-scheduledworkflow-7bbb6c9dc9-zbpx5     1/1     Running   0               19m
ml-pipeline-ui-b77595fcf-h9qgf                     1/1     Running   0               19m
ml-pipeline-viewer-crd-7c87784fcf-746sr            1/1     Running   0               19m
ml-pipeline-visualizationserver-754c5dd4dd-st6qh   1/1     Running   0               19m
mysql-55778745b6-q6znp                             1/1     Running   0               19m
training-operator-748d5cdc48-gffhk                 1/1     Running   22 (152m ago)   5d23h
workflow-controller-b7f95d6c6-c64tq                1/1     Running   0               19m
```

When everything is ready, you can run the following command to access the `ml-pipeline-ui` service.

```sh
$ kubectl get svc -n kubeflow ml-pipeline-ui
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
ml-pipeline-ui   ClusterIP   10.104.189.12   <none>        80/TCP    22m

$ kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
Forwarding from 127.0.0.1:8080 -> 3000
Forwarding from [::1]:8080 -> 3000
```

You can then open your browser and go to http://localhost:8080 to see the user interface.
