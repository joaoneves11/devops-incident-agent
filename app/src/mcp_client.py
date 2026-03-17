
import json
import os
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def _get_base_url() -> str:
    url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    return url.rstrip("/")


def _fetch(path: str):
    base = _get_base_url()
    try:
        with urlopen(f"{base}{path}", timeout=5) as resp:
            return json.loads(resp.read().decode())
    except (URLError, HTTPError, json.JSONDecodeError, OSError):
        return None


def get_logs(service: str | None = None):
    path = "/logs" if not service else f"/logs?service={service}"
    return _fetch(path) or []


def get_metrics():
    return _fetch("/metrics") or []


def get_deployments(service: str | None = None):
    path = "/deployments" if not service else f"/deployments?service={service}"
    return _fetch(path) or []


def _build_errors_summary(logs: list) -> dict:
    from collections import defaultdict
    by_service = defaultdict(lambda: defaultdict(int))
    for log in logs:
        if log.get("level") != "ERROR":
            continue
        service = log.get("service") or "unknown"
        error_type = log.get("error_type") or log.get("msg", "Unknown")[:50]
        by_service[service][error_type] += 1
    return {s: dict(e) for s, e in by_service.items()}


def fetch_mcp_context() -> str:
    logs = get_logs()
    metrics = get_metrics()
    deployments = get_deployments()

    parts = []

    if logs:
        summary = _build_errors_summary(logs)
        parts.append("### Resumo de erros por serviço (use para 'quais erros aparecem mais?')\n```json\n" + json.dumps(summary, indent=2, ensure_ascii=False) + "\n```")
        parts.append("### Logs recentes (ordem cronológica reversa)\n```json\n" + json.dumps(logs[-25:], indent=2, ensure_ascii=False) + "\n```")
    else:
        parts.append("### Logs e resumo\n(Sem dados ou MCP indisponível)")

    if metrics:
        parts.append("### Métricas atuais\n```json\n" + json.dumps(metrics if isinstance(metrics, list) else [metrics], indent=2, ensure_ascii=False) + "\n```")
    else:
        parts.append("### Métricas\n(Sem dados ou MCP indisponível)")

    if deployments:
        parts.append("### Deployments recentes (use para 'houve deploy recente?')\n```json\n" + json.dumps(deployments[-10:], indent=2, ensure_ascii=False) + "\n```")
    else:
        parts.append("### Deployments recentes\n(Sem dados ou MCP indisponível)")

    return "\n\n".join(parts)
