# Deploying to Azure Kubernetes Service (AKS)

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Docker](https://www.docker.com/) installed and running
- An active Azure subscription

---

## Step 1: Login to Azure

```powershell
az login
```

Set your subscription if you have multiple:

```powershell
az account set --subscription "<your-subscription-name-or-id>"
```

---

## Step 2: Create a Resource Group

```powershell
az group create --name k8s-test-rg --location eastus
```

---

## Step 3: Create an Azure Container Registry (ACR)

ACR is where your Docker image will be stored — AKS pulls from it.

```powershell
az acr create --resource-group k8s-test-rg --name k8stestregistry --sku Basic
```

> Registry name must be globally unique. Change `k8stestregistry` if it's taken.

Login to ACR:

```powershell
az acr login --name k8stestregistry
```

---

## Step 4: Build and Push the Image to ACR

```powershell
# Build and tag for ACR
docker build -t k8stestregistry.azurecr.io/k8s-apps-app:latest .

# Push to ACR
docker push k8stestregistry.azurecr.io/k8s-apps-app:latest
```

Verify it uploaded:

```powershell
az acr repository list --name k8stestregistry
```

---

## Step 5: Create an AKS Cluster

```powershell
az aks create `
  --resource-group k8s-test-rg `
  --name k8s-test-cluster `
  --node-count 2 `
  --generate-ssh-keys `
  --attach-acr k8stestregistry
```

> `--attach-acr` grants the cluster permission to pull images from your ACR automatically.

This takes a few minutes.

---

## Step 6: Connect kubectl to AKS

```powershell
az aks get-credentials --resource-group k8s-test-rg --name k8s-test-cluster
```

Verify the connection:

```powershell
kubectl get nodes
```

---

## Step 7: Update the Image in deployment.yaml

The AKS deployment uses your ACR image instead of the local one. Update `k8s/deployment.yaml`:

- Change `image` to `k8stestregistry.azurecr.io/k8s-apps-app:latest`
- Change `imagePullPolicy` from `Never` to `Always`

```yaml
image: k8stestregistry.azurecr.io/k8s-apps-app:latest
imagePullPolicy: Always
```

---

## Step 8: Deploy to AKS

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

Set the default namespace:

```powershell
kubectl config set-context --current --namespace=k8s-namespace
```

---

## Step 9: Expose the App Publicly

The minikube `NodePort` setup still works on AKS, but AKS supports `LoadBalancer` which gives a real public IP. Update `k8s/service.yaml`:

```yaml
spec:
  type: LoadBalancer
```

Then reapply:

```powershell
kubectl apply -f k8s/service.yaml
```

Wait for Azure to assign a public IP (takes ~1 minute):

```powershell
kubectl get service k8s-test-app -w
```

Once `EXTERNAL-IP` is no longer `<pending>`, access the app at:

```
http://<EXTERNAL-IP>:8001
```

---

## Step 10: Test the Endpoints

```powershell
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/health
curl http://<EXTERNAL-IP>:8001/ready
curl http://<EXTERNAL-IP>:8001/info
curl http://<EXTERNAL-IP>:8001/slow
```

---

## Step 11: Verify Load Balancing

Hit `/` multiple times — the `hostname` should rotate across pods:

```powershell
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/
```

---

## Step 12: Test Self-Healing

```powershell
# Terminal 1 — watch pods
kubectl get pods -w

# Terminal 2 — crash a pod
curl http://<EXTERNAL-IP>:8001/crash
```

Kubernetes will automatically restart the crashed pod.

---

## Teardown

Delete all Azure resources to avoid charges:

```powershell
az group delete --name k8s-test-rg --yes --no-wait
```

This deletes the resource group, AKS cluster, ACR, and everything inside them.
