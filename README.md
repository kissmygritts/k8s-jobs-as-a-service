## Colophon

```shell
uv init

touch worker.py controller.py Containerfile.worker Containerfile.controller deployment.yaml

uv add --group controller flask kubernetes

podman build -f Containerfile.controller -t k8s-jaas-controller:1.1 .
podman build -f Containerfile.worker -t k8s-jaas-worker .

## testing locally with kind
brew install kind

# Create local cluster
kind create cluster --name job-test

# Verify cluster
kubectl cluster-info --context kind-job-test

# building and pushing the controller image
podman build -f Containerfile.controller -t k8s-jaas-controller:1.1 .
podman save -o k8s-jaas-controller.tar k8s-jaas-controller:1.1
kind load image-archive k8s-jaas-controller.tar --name job-test

# building and pushing the worker image
podman build -f Containerfile.worker -t k8s-jaas-worker:1.0 .
podman save -o k8s-jaas-worker.tar k8s-jaas-worker:1.0
kind load image-archive k8s-jaas-worker.tar --name job-test

# verify images are loaded into kind
podman exec -it job-test-control-plane crictl images

# deploy 
kubectl apply -f deployment.yaml

# test it is working
# port forward
kubectl port-forward service/job-controller-service 8080:80

# in a different terminal start the following
kubectl get jobs -w

# then, in another terminal
curl http://localhost:8080/healthcheck

curl -X POST http://localhost:8080/submit-job \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from full deployment!"}'

# curl http://localhost/job-status/<jobid>
curl http://localhost:8080/job-status/

# delete if need to retry 
kubectl delete -f deployment.yaml
```

Troubleshooting `ImagePullBackoff` error

```shell
# building and pushing the controller image
podman build -f Containerfile.controller -t k8s-jaas-controller:1.1 .
podman save -o k8s-jaas-controller.tar k8s-jaas-controller:1.1
kind load image-archive k8s-jaas-controller.tar --name job-test

# check pods
kubectl get pods

# delete any for sanity reasons
kubectl delete pods --all

# run container within the cluster
kubectl run test-controller --image=localhost/k8s-jaas-controller:1.1 --image-pull-policy Never

# check container details
kubectl describe pods/test-controller

# make it testable
kubectl port-forward service/job-controller-service 8080:80
```