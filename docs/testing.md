# Testing the App on Kubernetes

## 1. Get the App URL

Run this in a terminal and keep it open — it creates a tunnel and prints the accessible URL:

```powershell
minikube service k8s-test-app -n k8s-namespace --url
```

Or open it directly in the browser:

```powershell
minikube service k8s-test-app -n k8s-namespace
```

## 2. Test Endpoints

Replace `<url>` with the URL from step 1 (e.g. `http://127.0.0.1:50944`).

```powershell
# Homepage — shows hostname of the pod that handled the request
curl <url>/

# Liveness probe
curl <url>/health

# Readiness probe
curl <url>/ready

# Pod info — shows POD_NAME, POD_NAMESPACE, APP_ENV
curl <url>/info

# Slow response — sleeps 3 seconds (controlled by SLOW_DELAY_SECONDS in ConfigMap)
curl <url>/slow
```

## 3. Verify Load Balancing

Hit `/` multiple times — the `hostname` in the response should rotate across all 3 pods:

```powershell
curl <url>/
curl <url>/
curl <url>/
```

## 4. Test Self-Healing

Crash a pod and watch Kubernetes restart it automatically:

```powershell
# In terminal 1 — watch pods
kubectl get pods -n k8s-namespace -w

# In terminal 2 — trigger a crash
curl <url>/crash
```

The pod status will briefly show `Error` then return to `Running`.

## 5. Check Cluster Health

```powershell
kubectl get pods -n k8s-namespace
kubectl get deployments -n k8s-namespace
kubectl get services -n k8s-namespace
kubectl describe pod -n k8s-namespace   # check liveness/readiness probe status
```
