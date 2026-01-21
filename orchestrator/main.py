from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langserve import RemoteRunnable, add_routes
from fastapi import FastAPI
from langchain_core.messages import BaseMessage
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import Body

class AgentState(TypedDict):
    messages: list[dict]
    #messages: Annotated[list[BaseMessage], "History"]

# Initialize connections to the 3 agents
agent1 = RemoteRunnable("http://localhost:8001/agent1/process")
agent2 = RemoteRunnable("http://localhost:8002/agent2/process")
agent3 = RemoteRunnable("http://localhost:8003/agent3/process")

async def call_a1(state):
    result = await agent1.ainvoke(state)
    print("[DEBUG] After call_a1, type:", type(result), "value:", result)
    return result

async def call_a2(state):
    result = await agent2.ainvoke(state)
    print("[DEBUG] After call_a2, type:", type(result), "value:", result)
    return result

async def call_a3(state):
    result = await agent3.ainvoke(state)
    print("[DEBUG] After call_a3, type:", type(result), "value:", result)
    return result

# Build Orchestration Graph
builder = StateGraph(AgentState)
builder.add_node("a1", call_a1)
builder.add_node("a2", call_a2)
builder.add_node("a3", call_a3)

builder.add_edge(START, "a1")
builder.add_edge("a1", "a2")
builder.add_edge("a2", "a3")
builder.add_edge("a3", END)

orchestrator_graph = builder.compile()

app = FastAPI(title="Master Orchestrator")
add_routes(app, orchestrator_graph, path="/orchestrate")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
