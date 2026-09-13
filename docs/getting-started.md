# Getting Started

## Prerequisites

- [minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- Docker installed and running
- Docker image `k8s-apps-app:latest` built locally via `docker compose build`

---

## Step 1: Start Minikube

```powershell
minikube start
```

Verify it's running:

```powershell
minikube status
```

---

## Step 2: Load the Docker Image into Minikube

Since the image is local and not on a registry, load it into minikube's Docker daemon:

```powershell
minikube image load k8s-apps-app:latest
```

Verify it loaded:

```powershell
minikube image ls
```

---

## Step 3: Apply the Kubernetes Manifests

Apply the namespace first, then all other resources:

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

---

## Step 4: Set Default Namespace

Avoid typing `-n k8s-namespace` on every command:

```powershell
kubectl config set-context --current --namespace=k8s-namespace
```

---

## Step 5: Verify Everything is Running

```powershell
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get nodes
```

All pods should show `Running` and `READY 1/1`. Deployment should show `3/3`.

---

## Step 6: Expose the App

Run this in a terminal and keep it open — it creates a tunnel to your local machine:

```powershell
minikube service k8s-test-app -n k8s-namespace --url
```

It will print a URL like `http://127.0.0.1:50944`. Use that URL in the steps below.

---

## Step 7: Test the Endpoints

Replace `<url>` with the URL from step 6.

```powershell
# Homepage — shows which pod handled the request
curl <url>/

# Liveness probe
curl <url>/health

# Readiness probe
curl <url>/ready

# Pod info — shows POD_NAME, POD_NAMESPACE, APP_ENV
curl <url>/info

# Slow response — sleeps 3 seconds
curl <url>/slow
```

---

## Step 8: Verify Load Balancing

Hit `/` multiple times — the `hostname` should rotate across the 3 pods:

```powershell
curl <url>/
curl <url>/
curl <url>/
```

---

## Step 9: Test Self-Healing

```powershell
# Terminal 1 — watch pods
kubectl get pods -w

# Terminal 2 — crash a pod
curl <url>/crash
```

The pod will briefly show `Error` then Kubernetes will restart it automatically.

---

## Teardown

```powershell
kubectl delete namespace k8s-namespace
minikube stop
```
