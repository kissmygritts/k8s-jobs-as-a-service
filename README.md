# Kubernetes Jobs as a Service

A lightweight Kubernetes pattern for running CPU-intensive batch workloads on-demand via HTTP APIs. Submit jobs through a simple REST endpoint, and Kubernetes automatically provisions isolated containers with dedicated resources to execute

## Getting Started

Install the following (I'm using a mac):

- Homebrew
- podman (or Docker)
- kubectl
- kind (or minikube)
- uv

Then

```shell
git clone ...
cd k8s-job-as-a-service

# start podman, follow prompts printed to the terminal
podman machine init

# once that is complete, start kind
kind create cluster --name job-test

# verify cluster
kubectl cluster-info --context kind-job-test
```

## Build Images

This part will be different if using Docker. 

```shell
# building and pushing the controller image
podman build -f Containerfile.controller -t k8s-jaas-controller:1.0 .
# in order to load the image to the kind cluster save as a .tar archive
podman save -o k8s-jaas-controller.tar k8s-jaas-controller:1.0
# then load into kind
kind load image-archive k8s-jaas-controller.tar --name job-test

# building and pushing the worker image
podman build -f Containerfile.worker -t k8s-jaas-worker:1.0 .
podman save -o k8s-jaas-worker.tar k8s-jaas-worker:1.0
kind load image-archive k8s-jaas-worker.tar --name job-test

# verify images are loaded into kind
podman exec -it job-test-control-plane crictl images
```

## Test Locally

```shell
# deploy 
kubectl apply -f deployment.yaml

# test it is working, in one terminal run a port forwarding service
kubectl port-forward service/job-controller-service 8080:80

# in a different terminal start the following to watch jobs as they are run
kubectl get jobs -w

# then, in another terminal run the healthcheck to make sure things are wired up
curl http://localhost:8080/healthcheck

# create a job
curl -X POST http://localhost:8080/submit-job \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from full deployment!"}'

# check the job status
curl http://localhost/job-status/<jobid>

# for more detailed information about the jobs, etc
kubectl describe pods/test-controller

# logs for the job
kubectl logs job.batch/<job name>

# delete if need to retry 
kubectl delete -f deployment.yaml
kubectl delete pods --all
kubectl delete services --all
kubectl delete jobs --all
```
<details>
  <summary>Colophon</summary>

  ```shell
    uv init

    touch worker.py controller.py Containerfile.worker Containerfile.controller deployment.yaml

    uv add --group controller flask kubernetes

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

    curl http://localhost/job-status/<jobid>

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
</details>