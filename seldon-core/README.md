### Install kubenetes
```sh
$ kubectl cluster-info 
Kubernetes control plane is running at https://localhost:8443
CoreDNS is running at https://localhost:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

### Install helm
```sh
$ wget https://get.helm.sh/helm-v3.10.0-linux-amd64.tar.gz
$ tar xvzf helm-v3.10.0-linux-amd64.tar.gz
$ sudo mv linux-amd64/helm /usr/local/bin/helm
$ helm
The Kubernetes package manager

Common actions for Helm:

- helm search:    search for charts
- helm pull:      download a chart to your local directory to view
- helm install:   upload the chart to Kubernetes
- helm list:      list releases of charts
...
```

### Install s2i
```sh
$ wget https://github.com/openshift/source-to-image/releases/download/v1.3.1/source-to-image-v1.3.1-a5a77147-linux-amd64.tar.gz

$ tar xvzf source-to-image-v1.3.1-a5a77147-linux-amd64.tar.gz

$ sudo cp s2i /usr/local/bin/
```

### Install istio ingress
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

### Install seldon-core
```sh
$ kubectl create namespace seldon-system
namespace/seldon-system created

$ helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set istio.enabled=true \
    --namespace seldon-system
NAME: seldon-core
LAST DEPLOYED: Mon Oct 24 21:16:49 2022
NAMESPACE: seldon-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

### Verify
```
$ kubectl get pods -n istio-system 
NAME                                    READY   STATUS    RESTARTS       AGE
istio-ingressgateway-58fbb84dfd-d72nz   1/1     Running   0              12h
istiod-77f69cccd6-t9grw                 1/1     Running   52 (22h ago)   29d

$ kubectl get pods -n seldon-system 
NAME                                         READY   STATUS    RESTARTS   AGE
seldon-controller-manager-59d8b884b4-v9btz   1/1     Running   0          5m43s
```