from fastapi import FastAPI
from langserve import add_routes
from langchain_core.runnables import RunnableLambda
import uvicorn

# Agent 1 configuration (hardcoded)
AGENT_ID = "3"
PORT = 8003

app = FastAPI(title="Worker Agent {AGENT_ID}")

def process_logic(state: dict):
    """Specific logic for agent_3 node."""
    print("Entered agent_3 process_logic with state:", state)
    last_msg = state['messages'][-1]['content']
    prompt = f"System: You are Agent 3. Processing: {last_msg}"
    state['messages'][-1][AGENT_ID] = 'INVOKED'
    return state

# Expose as a LangServe route for agent_1
add_routes(app, RunnableLambda(process_logic), path="/agent{AGENT_ID}/process")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
