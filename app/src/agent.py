from .graph import run_graph


def run_agent(query: str, **kwargs) -> str:
    return run_graph(
        query,
        top_k=kwargs.get("top_k", 3),
        temperature=kwargs.get("temperature", 0.2),
    )
