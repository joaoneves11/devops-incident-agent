import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="DevOps Incident MCP Server")
DATA_DIR = Path(__file__).parent / "data"


def load_json(name: str):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


@app.get("/logs")
def get_logs(service: str | None = None):
    data = load_json("logs")
    if service:
        data = [e for e in data if e.get("service") == service]
    return JSONResponse(content=data)


@app.get("/metrics")
def get_metrics():
    return JSONResponse(content=load_json("metrics"))


@app.get("/deployments")
def get_deployments(service: str | None = None):
    data = load_json("deployments")
    if service:
        data = [e for e in data if e.get("service") == service]
    return JSONResponse(content=data)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MCP_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
