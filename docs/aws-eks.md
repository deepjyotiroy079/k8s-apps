# Deploying to Amazon Elastic Kubernetes Service (EKS)

## Prerequisites

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
- [eksctl](https://eksctl.io/installation/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Docker](https://www.docker.com/) installed and running
- An active AWS account

---

## Step 1: Configure AWS CLI

```powershell
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, region (e.g. `us-east-1`), and output format (`json`).

Verify login:

```powershell
aws sts get-caller-identity
```

---

## Step 2: Create an ECR Repository

ECR (Elastic Container Registry) is where your Docker image will be stored.

```powershell
aws ecr create-repository --repository-name k8s-apps-app --region us-east-1
```

Note the `repositoryUri` from the output — it will look like:

```
<account-id>.dkr.ecr.us-east-1.amazonaws.com/k8s-apps-app
```

---

## Step 3: Build and Push the Image to ECR

Login to ECR:

```powershell
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

Build and push:

```powershell
# Build and tag for ECR
docker build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/k8s-apps-app:latest .

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/k8s-apps-app:latest
```

Verify it uploaded:

```powershell
aws ecr list-images --repository-name k8s-apps-app --region us-east-1
```

---

## Step 4: Create an EKS Cluster

```powershell
eksctl create cluster `
  --name k8s-test-cluster `
  --region us-east-1 `
  --nodes 2 `
  --node-type t3.small
```

> This takes 10–15 minutes. eksctl also configures kubectl automatically.

Verify the cluster:

```powershell
kubectl get nodes
```

---

## Step 5: Grant EKS Access to ECR

EKS nodes need permission to pull from ECR. Attach the ECR policy to the node group IAM role:

```powershell
# Get the node group role name
$ROLE_NAME = aws eks describe-nodegroup `
  --cluster-name k8s-test-cluster `
  --nodegroup-name $(aws eks list-nodegroups --cluster-name k8s-test-cluster --query 'nodegroups[0]' --output text) `
  --query 'nodegroup.nodeRole' --output text | Split-Path -Leaf

# Attach ECR read-only policy
aws iam attach-role-policy `
  --role-name $ROLE_NAME `
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

---

## Step 6: Update the Image in deployment.yaml

Update `k8s/deployment.yaml` to use your ECR image:

```yaml
image: <account-id>.dkr.ecr.us-east-1.amazonaws.com/k8s-apps-app:latest
imagePullPolicy: Always
```

---

## Step 7: Deploy to EKS

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

Set the default namespace:

```powershell
kubectl config set-context --current --namespace=k8s-namespace
```

---

## Step 8: Expose the App Publicly

Update `k8s/service.yaml` to use `LoadBalancer` — AWS will provision an Elastic Load Balancer automatically:

```yaml
spec:
  type: LoadBalancer
```

Reapply:

```powershell
kubectl apply -f k8s/service.yaml
```

Wait for the external hostname to be assigned (takes ~2 minutes):

```powershell
kubectl get service k8s-test-app -w
```

Once `EXTERNAL-IP` shows a hostname (e.g. `abc123.us-east-1.elb.amazonaws.com`), access the app at:

```
http://<EXTERNAL-IP>:8001
```

---

## Step 9: Test the Endpoints

```powershell
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/health
curl http://<EXTERNAL-IP>:8001/ready
curl http://<EXTERNAL-IP>:8001/info
curl http://<EXTERNAL-IP>:8001/slow
```

---

## Step 10: Verify Load Balancing

Hit `/` multiple times — the `hostname` should rotate across pods:

```powershell
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/
curl http://<EXTERNAL-IP>:8001/
```

---

## Step 11: Test Self-Healing

```powershell
# Terminal 1 — watch pods
kubectl get pods -w

# Terminal 2 — crash a pod
curl http://<EXTERNAL-IP>:8001/crash
```

Kubernetes will automatically restart the crashed pod.

---

## Teardown

Delete all AWS resources to avoid charges:

```powershell
# Delete the EKS cluster and node group
eksctl delete cluster --name k8s-test-cluster --region us-east-1

# Delete the ECR repository
aws ecr delete-repository --repository-name k8s-apps-app --region us-east-1 --force
```
