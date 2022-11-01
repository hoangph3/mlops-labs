export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo $INGRESS_HOST

cd ./proto/ && grpcurl -d "`cat ../payload.json`" \
-rpc-header seldon:mnist-classifier -rpc-header namespace:seldon-model \
-plaintext \
-proto ./prediction.proto $INGRESS_HOST:80 seldon.protos.Seldon/Predict