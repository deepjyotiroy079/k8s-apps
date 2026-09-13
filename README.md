# K8s Test App

A simple FastAPI app built for testing Kubernetes features locally with minikube.

## Features

| Endpoint | Purpose |
|---|---|
| `GET /` | Returns hostname — useful for verifying load balancing across pods |
| `GET /health` | Liveness probe |
| `GET /ready` | Readiness probe |
| `GET /info` | Shows pod name, namespace, and injected env vars |
| `GET /slow` | Sleeps for `SLOW_DELAY_SECONDS` (default 3s) — for testing timeouts |
| `GET /crash` | Exits the process — for testing pod restarts |

## Project Structure

```
k8s-apps/
├── main.py               # FastAPI app
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image
├── docker-compose.yml    # Local Docker run
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml   # 3 replicas, liveness/readiness probes
│   └── service.yaml      # NodePort
└── docs/
    ├── getting-started.md
    └── testing.md
```

## Quick Start

See [docs/getting-started.md](docs/getting-started.md) for the full step-by-step guide.

### Run Locally

```powershell
pip install -r requirements.txt
python main.py
```

### Run with Docker

```powershell
docker compose up --build
```

### Deploy to Minikube

```powershell
minikube start
minikube image load k8s-apps-app:latest
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
kubectl config set-context --current --namespace=k8s-namespace
minikube service k8s-test-app -n k8s-namespace
```

## Requirements

- Python 3.12+
- Docker
- minikube
- kubectl
