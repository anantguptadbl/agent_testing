from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langserve import RemoteRunnable, add_routes
from fastapi import FastAPI
from langchain_core.messages import BaseMessage
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import Body
import requests


class AgentState(TypedDict):
    messages: list[dict]
    # messages: Annotated[list[BaseMessage], "History"]


# Initialize connections to the 3 agents
agent1 = RemoteRunnable("http://localhost:8001/agent1/process")
agent2 = RemoteRunnable("http://localhost:8002/agent2/process")
agent3 = RemoteRunnable("http://localhost:8003/agent3/process")


def call_api1(state):
    url = "http://127.0.0.1:8004/api1/getdata1"
    params = {"input": "hello"}
    print("[DEBUG] Calling API1 with URL:", url, "and params:", params)
    print("Value of url and params:", url, params)
    response = requests.get(url, params=params)
    print("[DEBUG] Getting AP1 response json:", response.json())
    state["messages"].append(response.json())
    print("[DEBUG] State in AP1:", state)
    return state


def call_a1(state):
    print("[DEBUG] In call_a1 with state:", state)
    if state["messages"][-1]["content"] == "hello":
        result = agent1.invoke(state)
        print("[DEBUG] After call_a1, type:", type(result), "value:", result)
        return result
    return state


def call_a2(state):
    result = agent2.invoke(state)
    print("[DEBUG] After call_a2, type:", type(result), "value:", result)
    return result


def call_a3(state):
    result = agent3.invoke(state)
    print("[DEBUG] After call_a3, type:", type(result), "value:", result)
    return result


# Build Orchestration Graph

builder = StateGraph(AgentState)
builder.add_node("api1", call_api1)
builder.add_node("a1", call_a1)
builder.add_node("a2", call_a2)
builder.add_node("a3", call_a3)

builder.add_edge(START, "api1")
builder.add_edge("api1", "a1")
builder.add_edge("a1", "a2")
builder.add_edge("a2", "a3")
builder.add_edge("a3", END)


def build_orchestrator_graph(builder_object):
    """
    Takes a builder object and returns a compiled orchestrator graph instance.
    """
    return builder_object.compile()


orchestrator_graph = build_orchestrator_graph(builder)

app = FastAPI(title="Master Orchestrator")
add_routes(app, orchestrator_graph, path="/orchestrate")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
