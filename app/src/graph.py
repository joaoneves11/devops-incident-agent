import json
import os
from typing import Literal, TypedDict

from openai import OpenAI

from .guardrails import apply_guardrails
from .prompts import get_system_prompt_for_tools, get_user_prompt
from .rag import retrieve
from .tools import OPENAI_TOOLS, execute_tool

# Estado compartilhado do grafo
class AgentState(TypedDict, total=False):
    query: str
    top_k: int
    temperature: float
    rag_context: str
    system_prompt: str
    raw_response: str
    final_response: str


def _get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Set it in .env or your environment."
        )
    return OpenAI(api_key=api_key)


def node_fetch_rag(state: AgentState) -> dict:
    query = state["query"]
    top_k = state.get("top_k", 3)
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {"rag_context": ""}
    parts = [f"## {name}\n{content}" for name, content in chunks]
    return {"rag_context": "\n\n".join(parts)}


def node_build_prompts_for_tools(state: AgentState) -> dict:
    system_prompt = get_system_prompt_for_tools(rag_context=state.get("rag_context", ""))
    return {"system_prompt": system_prompt}


def node_agent_loop(state: AgentState) -> dict:
    
    client = _get_openai_client()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    temperature = state.get("temperature", 0.2)

    messages = [
        {"role": "system", "content": state["system_prompt"]},
        {"role": "user", "content": get_user_prompt(state["query"])},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
            temperature=temperature,
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            raw = (msg.content or "").strip()
            return {"raw_response": raw}
        # Anexar mensagem do assistente com tool_calls
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments or "{}"}}
                for tc in msg.tool_calls
            ],
        })
        # Executar cada ferramenta e anexar resultado
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


def _should_refine(state: AgentState) -> Literal["refine_analysis", "apply_guardrails"]:
    raw = (state.get("raw_response") or "").lower()
    if "hipótese" in raw or "causa raiz" in raw or "root cause" in raw or "hypothes" in raw:
        return "apply_guardrails"
    return "refine_analysis"


def node_refine_analysis(state: AgentState) -> dict:
    client = _get_openai_client()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    temperature = state.get("temperature", 0.2)
    prev = state.get("raw_response", "")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": state["system_prompt"]},
            {"role": "user", "content": f"Análise anterior do agente:\n\n{prev}\n\nRefine a resposta incluindo uma seção **Hipóteses de causa raiz** (1-3 itens) e mantendo **Passos recomendados** claros. Mantenha o mesmo idioma. Seja conciso."},
        ],
        temperature=temperature,
    )
    refined = (response.choices[0].message.content or "").strip()
    return {"raw_response": refined}


def node_apply_guardrails(state: AgentState) -> dict:
    final = apply_guardrails(state.get("raw_response", ""))
    return {"final_response": final}


def build_graph():
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(AgentState)

    builder.add_node("fetch_rag", node_fetch_rag)
    builder.add_node("build_prompts_for_tools", node_build_prompts_for_tools)
    builder.add_node("agent_loop", node_agent_loop)
    builder.add_node("refine_analysis", node_refine_analysis)
    builder.add_node("apply_guardrails", node_apply_guardrails)

    builder.add_edge(START, "fetch_rag")
    builder.add_edge("fetch_rag", "build_prompts_for_tools")
    builder.add_edge("build_prompts_for_tools", "agent_loop")
    builder.add_conditional_edges("agent_loop", _should_refine, {"refine_analysis": "refine_analysis", "apply_guardrails": "apply_guardrails"})
    builder.add_edge("refine_analysis", "apply_guardrails")
    builder.add_edge("apply_guardrails", END)

    return builder.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_graph(query: str, top_k: int = 3, temperature: float = 0.2) -> str:
    graph = get_graph()
    initial: AgentState = {
        "query": query,
        "top_k": top_k,
        "temperature": temperature,
    }
    result = graph.invoke(initial)
    return result.get("final_response", "")
