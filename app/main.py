
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.agent import run_agent

app = FastAPI(title="DevOps Incident Agent")


class IncidentQuery(BaseModel):
    query: str
    top_k: int = 3
    temperature: float = 0.2


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"service": "devops-incident-agent"}


@app.post("/ask")
def ask(query: IncidentQuery):
    """Envia uma pergunta/incidente e retorna a resposta do agente (OpenAI + RAG + guardrails)."""
    try:
        response = run_agent(
            query.query,
            top_k=query.top_k,
            temperature=query.temperature,
        )
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
