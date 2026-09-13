import os
import sys
import time
import socket
from fastapi import FastAPI

app = FastAPI(title="K8s Test App")


@app.get("/")
def read_root():
    return {
        "message": "Hello, World!",
        "hostname": socket.gethostname(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/info")
def info():
    return {
        "hostname": socket.gethostname(),
        "pod_name": os.getenv("POD_NAME", "unknown"),
        "namespace": os.getenv("POD_NAMESPACE", "unknown"),
        "env": {k: v for k, v in os.environ.items() if k.startswith("APP_")},
    }


@app.get("/crash")
def crash():
    sys.exit(1)


@app.get("/slow")
def slow():
    delay = float(os.getenv("SLOW_DELAY_SECONDS", "3"))
    time.sleep(delay)
    return {"slept": delay}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
