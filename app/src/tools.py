
import json

from .mcp_client import get_logs as mcp_get_logs
from .mcp_client import get_metrics as mcp_get_metrics
from .mcp_client import get_deployments as mcp_get_deployments


# Definição no formato OpenAI (function calling)
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Busca logs recentes no MCP server. Opcionalmente filtra por nome do serviço (ex.: payments-api, orders-api) para investigar um serviço específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Opcional. Filtra logs pelo nome do serviço (ex.: payments-api). Omita para obter todos os logs.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_metrics",
            "description": "Busca metrics atuais (erros, latência, pool de DB, Kafka lag, etc.) no MCP server.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_deployments",
            "description": "Busca deployments recentes no MCP server. Opcionalmente filtra por serviço para verificar se um serviço específico teve deploy recentemente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Opcional. Filtra deployments pelo nome do serviço. Omita para obter todos os deployments recentes.",
                    }
                },
            },
        },
    },
]


def execute_tool(name: str, arguments: dict) -> str:
  
    if name == "get_logs":
        service = arguments.get("service") if isinstance(arguments, dict) else None
        data = mcp_get_logs(service=service)
        return json.dumps(data[-30:], indent=2, ensure_ascii=False)
    if name == "get_metrics":
        data = mcp_get_metrics()
        return json.dumps(data if isinstance(data, list) else [data], indent=2, ensure_ascii=False)
    if name == "get_deployments":
        service = arguments.get("service") if isinstance(arguments, dict) else None
        data = mcp_get_deployments(service=service)
        return json.dumps(data[-15:], indent=2, ensure_ascii=False)
    return json.dumps({"error": f"Ferramenta desconhecida: {name}"})
