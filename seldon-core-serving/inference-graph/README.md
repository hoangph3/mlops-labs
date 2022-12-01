# Serving your Models in a Pipeline

## Setup environments
1. Install and setup Istio
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

3. Create namespace `seldon-model` and setup an istio gateway
```sh
$ kubectl create namespace seldon-model
namespace/seldon-model created

$ kubectl label namespace seldon-model istio-injection=enabled
namespace/seldon-model labeled

$ kubectl get ns seldon-model --show-labels
NAME           STATUS   AGE   LABELS
seldon-model   Active   28s   istio-injection=enabled,kubernetes.io/metadata.name=seldon-model

$ kubectl apply -f seldon-gateway.yaml
gateway.networking.istio.io/seldon-gateway created
```

4. Create a `seldon-system` namespace and install Seldon Core.
```sh
$ kubectl create namespace seldon-system
namespace/seldon-system created

$ kubectl config set-context --current --namespace=seldon-system
Context "minikube" modified.

$ kubectl get pods
No resources found in seldon-system namespace.

$ git clone https://github.com/SeldonIO/seldon-core
$ cd seldon-core
$ git checkout v1.14.1
$ git branch
* (HEAD detached at v1.14.1)
  master

$ cd helm-charts/

# Generate the manifests file to deploy seldon-core
$ helm template --output-dir ./yamls  seldon-core-operator/
wrote ./yamls/seldon-core-operator/templates/serviceaccount_seldon-manager.yaml
wrote ./yamls/seldon-core-operator/templates/webhook.yaml
wrote ./yamls/seldon-core-operator/templates/configmap_seldon-config.yaml
wrote ./yamls/seldon-core-operator/templates/customresourcedefinition_v1_seldondeployments.machinelearning.seldon.io.yaml
wrote ./yamls/seldon-core-operator/templates/clusterrole_seldon-manager-role.yaml
wrote ./yamls/seldon-core-operator/templates/clusterrole_seldon-manager-sas-role.yaml
wrote ./yamls/seldon-core-operator/templates/clusterrolebinding_seldon-manager-rolebinding.yaml
wrote ./yamls/seldon-core-operator/templates/clusterrolebinding_seldon-manager-sas-rolebinding.yaml
wrote ./yamls/seldon-core-operator/templates/role_seldon-leader-election-role.yaml
wrote ./yamls/seldon-core-operator/templates/rolebinding_seldon-leader-election-rolebinding.yaml
wrote ./yamls/seldon-core-operator/templates/service_seldon-webhook-service.yaml
wrote ./yamls/seldon-core-operator/templates/deployment_seldon-controller-manager.yaml
wrote ./yamls/seldon-core-operator/templates/webhook.yaml

# Update ISTIO_ENABLED=true
$ nano yamls/seldon-core-operator/templates/deployment_seldon-controller-manager.yaml

# Create the manifests
$ kubectl create -f yamls/seldon-core-operator/templates/
clusterrole.rbac.authorization.k8s.io/seldon-manager-role-seldon-system created
clusterrole.rbac.authorization.k8s.io/seldon-manager-sas-role-seldon-system created
clusterrolebinding.rbac.authorization.k8s.io/seldon-manager-rolebinding-seldon-system created
clusterrolebinding.rbac.authorization.k8s.io/seldon-manager-sas-rolebinding-seldon-system created
configmap/seldon-config created
customresourcedefinition.apiextensions.k8s.io/seldondeployments.machinelearning.seldon.io created
deployment.apps/seldon-controller-manager created
role.rbac.authorization.k8s.io/seldon-leader-election-role created
rolebinding.rbac.authorization.k8s.io/seldon-leader-election-rolebinding created
service/seldon-webhook-service created
serviceaccount/seldon-manager created
secret/seldon-webhook-server-cert created
validatingwebhookconfiguration.admissionregistration.k8s.io/seldon-validating-webhook-configuration-seldon-system created
```

5. Verify
```sh
# set default namespace
$ kubectl config set-context --current --namespace=default
Context "minikube" modified.

$ kubectl get pods -n istio-system
NAME                                    READY   STATUS    RESTARTS   AGE
istio-ingressgateway-859d74978f-w7wqm   1/1     Running   0          20m
istiod-64699c7b75-rb9fb                 1/1     Running   0          20m

$ kubectl get pods -n seldon-system
NAME                                         READY   STATUS    RESTARTS   AGE
seldon-controller-manager-59d8b884b4-pgnnj   1/1     Running   0          9s
```

## Build inference pipeline

1. Build image for each component
```
$ python3 build_component.py
```

2. Validate
```
$ docker images | grep seldon | grep hoang
hoangph3/seldon-sentiment-analysis               v0.0.1         db580a87ede5   39 seconds ago   242MB
hoangph3/seldon-text-tagging                     v0.0.1         8ed0623d8aa1   43 seconds ago   613MB
hoangph3/seldon-summarize-text                   v0.0.1         cda1d68390bf   47 seconds ago   441MB
```

3. Run inference pipeline from manifest
```yaml
---
apiVersion: machinelearning.seldon.io/v1alpha2
kind: SeldonDeployment
metadata:
  labels:
    app: seldon
  name: seldon-pipeline
  namespace: seldon-model
spec:
  annotations:
    project_name: seldon-pipeline
    deployment_version: v0.0.1
    seldon.io/rest-read-timeout: '100000'
    seldon.io/rest-connection-timeout: '100000'
    seldon.io/grpc-read-timeout: '100000'
  name: seldon-pipeline
  oauth_key: oauth-key
  oauth_secret: oauth-secret
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - name: sentiment-analysis
          image: hoangph3/seldon-sentiment-analysis:v0.0.1
          imagePullPolicy: IfNotPresent
        - name: text-tagging
          image: hoangph3/seldon-text-tagging:v0.0.1
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: false
            runAsUser: 0
        - name: summarize-text
          image: hoangph3/seldon-summarize-text:v0.0.1
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: false
            runAsUser: 0
        terminationGracePeriodSeconds: 20
    graph:
      children:
      - name: text-tagging
        endpoint:
          type: REST
        type: MODEL
        children:
        - name: summarize-text
          endpoint:
            type: REST
          type: MODEL
          children: []
      name: sentiment-analysis
      endpoint:
        type: REST
      type: MODEL
    name: example
    replicas: 1
    annotations:
      predictor_version: v1
```

```sh
$ kubectl apply -f deploy-model.yml
seldondeployment.machinelearning.seldon.io/seldon-pipeline created

$ kubectl get pods -n seldon-model 
NAME                                                       READY   STATUS    RESTARTS   AGE
seldon-c4888704f0b4934a7cbd2df09d86d3da-7df5dd4f99-jl887   5/5     Running   0          119s
```

Note that in this case, we have three pods corresponding to three components (`sentiment-analysis`, `text-tagging`, `summarize-text`), one pod is `seldon-container-engine`, and the last one is `istio-proxy`.

## Testing

1. Firstly, start an external load balancer:
```sh
$ minikube tunnel
Status:	
	machine: minikube
	pid: 15766
	route: 10.96.0.0/12 -> 192.168.0.5
	minikube: Running
	services: [istio-ingressgateway]
    errors: 
		minikube: no errors
		router: no errors
		loadbalancer emulator: no errors
```

1. Make a prediction after the Seldon Deployment is available via the ingress gateway created.
```sh
$ export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

$ echo $INGRESS_HOST
10.106.254.233

$ curl -X POST -d @payload.json -H 'Content-Type: application/json' \
    http://$INGRESS_HOST/seldon/seldon-model/seldon-pipeline/api/v1.0/predictions | json_pp

{
  "data": {
    "names": [],
    "ndarray": [
      "In an attempt to build an AI-ready workforce, Microsoft announced Intelligent Cloud Hub which has been launched to empower the next generation of students with AI-ready skills. Envisioned as a three-year collaborative program, Intelligent Cloud Hub will support around 100 institutions with AI infrastructure, course content and curriculum, developer support, development tools and give students access to cloud and AI services. As part of the program, the Redmond giant which wants to expand its reach and is planning to build a strong developer ecosystem in India with the program will set up the core AI infrastructure and IoT Hub for the selected campuses. The company will provide AI development tools and Azure AI services such as Microsoft Cognitive Services, Bot Services and Azure Machine Learning. According to Manish Prakash, Country General Manager-PS, Health and Education, Microsoft India, said, With AI being the defining technology of our time, it is transforming lives and industry and the jobs of tomorrow will require a different skillset. This will require more collaborations and training and working with AI. That’s why it has become more critical than ever for educational institutions to integrate new cloud and AI technologies. The program is an attempt to ramp up the institutional set-up and build capabilities among the educators to educate the workforce of tomorrow. The program aims to build up the cognitive skills and in-depth understanding of developing intelligent cloud connected solutions for applications across industry. Earlier in April this year, the company announced Microsoft Professional Program In AI as a learning track open to the public. The program was developed to provide job ready skills to programmers who wanted to hone their skills in AI and data science with a series of online courses which featured hands-on labs and expert instructors as well. This program also included developer-focused AI school that provided a bunch of assets to help build AI skills"
    ]
  },
  "meta": {
    "requestPath": {
      "sentiment-analysis": "hoangph3/seldon-sentiment-analysis:v0.0.1",
      "summarize-text": "hoangph3/seldon-summarize-text:v0.0.1",
      "text-tagging": "hoangph3/seldon-text-tagging:v0.0.1"
    },
    "tags": {
      "input_text": "In an attempt to build an AI-ready workforce, Microsoft announced Intelligent Cloud Hub which has been launched to empower the next generation of students with AI-ready skills. Envisioned as a three-year collaborative program, Intelligent Cloud Hub will support around 100 institutions with AI infrastructure, course content and curriculum, developer support, development tools and give students access to cloud and AI services. As part of the program, the Redmond giant which wants to expand its reach and is planning to build a strong developer ecosystem in India with the program will set up the core AI infrastructure and IoT Hub for the selected campuses. The company will provide AI development tools and Azure AI services such as Microsoft Cognitive Services, Bot Services and Azure Machine Learning. According to Manish Prakash, Country General Manager-PS, Health and Education, Microsoft India, said, With AI being the defining technology of our time, it is transforming lives and industry and the jobs of tomorrow will require a different skillset. This will require more collaborations and training and working with AI. That’s why it has become more critical than ever for educational institutions to integrate new cloud and AI technologies. The program is an attempt to ramp up the institutional set-up and build capabilities among the educators to educate the workforce of tomorrow. The program aims to build up the cognitive skills and in-depth understanding of developing intelligent cloud connected solutions for applications across industry. Earlier in April this year, the company announced Microsoft Professional Program In AI as a learning track open to the public. The program was developed to provide job ready skills to programmers who wanted to hone their skills in AI and data science with a series of online courses which featured hands-on labs and expert instructors as well. This program also included developer-focused AI school that provided a bunch of assets to help build AI skills",
      "sentiment_analysis_passed": true,
      "sentiment_analysis_result": {
        "compound": 0.9769,
        "neg": 0.008,
        "neu": 0.891,
        "pos": 0.101
      },
      "summarize_text_passed": true,
      "summarize_text_result": "[' As part of the program, the Redmond giant which wants to expand its reach and is planning to build a strong developer ecosystem in India with the program will set up the core AI infrastructure and IoT Hub for the selected campuses', ' The program was developed to provide job ready skills to programmers who wanted to hone their skills in AI and data science with a series of online courses which featured hands-on labs and expert instructors as well']",
      "tags": "['#collaboration', '#skillset', '#different', '#life', '#transforming']",
      "text_tagging_passed": true
    }
  }
}
```