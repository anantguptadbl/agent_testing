from typing import TypedDict
import uuid
from langserve import RemoteRunnable
import openai
import requests


class AgentState(TypedDict):
    messages: list[dict]
    # messages: Annotated[list[BaseMessage], "History"]


# Initialize connections to the 3 agents
agent1 = RemoteRunnable("http://localhost:8001/agent1/process")
agent2 = RemoteRunnable("http://localhost:8002/agent2/process")
agent3 = RemoteRunnable("http://localhost:8003/agent3/process")
agent4 = RemoteRunnable("http://localhost:8003/agent4/process")
agent5 = RemoteRunnable("http://localhost:8003/agent5/process")


def call_api1(state):
    url = "http://127.0.0.1:8004/api1/getdata1"
    params = {"input": "hello"}
    response = requests.post(url, params=params)
    print("[DEBUG] In call_api1 with state: {} and type of state is ", state, type(state))
    state["messages"].append(response.json())
    return state


def call_a1(state):
    print("[DEBUG] In call_a1 with state:", state)
    if state["messages"][-1]["content"] == "hello":
        result = agent1.invoke(state)
        print("[DEBUG] After call_a1, type:", type(result), "value:", result)
        return result
    return state


def call_a2(state):
    print("[DEBUG] In call_a2 with state:", state)
    result = agent2.invoke(state)
    print("[DEBUG] After call_a2, type:", type(result), "value:", result)
    return result


def call_a3(state):
    # Check if 'Processed by agent3' already present
    already_processed = any(
        msg.get("content") == "Processed by agent3" for msg in state["messages"]
    )
    print(f"[DEBUG] In call_a3 with state {state}: and already_processed:", already_processed)
    if not already_processed:
        result = agent3.invoke(state)
        result["messages"].append({"role": "system", "content": "Processed by agent3", "uuid": uuid.uuid4().hex})
    print("[DEBUG] After call_a3, type:", type(result), "value:", result)
    return result

def call_a4(state):
    result = agent4.batch(state)
    result["messages"].append({"role": "system", "content": "Processed by agent4", "uuid": uuid.uuid4().hex})
    print("[DEBUG] After call_a4, type:", type(result), "value:", result)
    return result

def call_a5(state):
    result = agent5.batch(state)
    print("[DEBUG] After call_a5, type:", type(result), "value:", result)
    return result


# --- LLM-driven Orchestration ---
openai.api_key = ""  # Replace with your actual key or use os.environ

AGENT_FUNCTIONS = {
    "api1": call_api1,
    "a1": call_a1,
    "a2": call_a2,
    "a3": call_a3,
    "a4": call_a4,
    "a5": call_a5,
}

def query_llm_for_next_agent(state, history):
    """
    Query OpenAI LLM to decide the next agent and action.
    """
    prompt = f"""
    You are an orchestrator for agentic workflows.You need to generate the next_agent name 
    The order of agent execution is api1 -> a1 -> a2 -> a3 -> end
    If the history shows that there is user and api1 role only then output a1
    If the history shows that a1 has completed processing done then output a2
    If the history shows that a1 and a2 has completed processing done then output a3
    If the history shows that a1, a2 and a3 has completed processing done then output end
    Current state: {state}
    History: {history}
    Respond with a JSON object: {{'next_agent': 'agent_name'}}. If finished, set next_agent to 'end'.
    """
    from openai import OpenAI
    client = OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "system", "content": "You are an agentic orchestrator."},
                  {"role": "user", "content": prompt}],
        temperature=0
    )
    import json
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
    except Exception:
        result = {'next_agent': 'end'}
    return result

def run_llm_orchestrator(initial_state):
    state = initial_state
    history = []
    results = {}
    current_agent = "api1"  # Start with api1 or as decided
    while current_agent != "end":
        print(f"[DEBUG] ORCHESTRATOR CODE : Current agent: {current_agent}, state: {state}, history: {history}")
        agent_func = AGENT_FUNCTIONS.get(current_agent)
        if agent_func is None:
            break
        result = agent_func(state)
        results[current_agent] = result
        history.append({"agent": current_agent, "result": result})
        state = result if isinstance(result, dict) else state
        print(f"[DEBUG] After {current_agent}, state: {state}, history: {history}")
        llm_decision = query_llm_for_next_agent(state, history)
        print(f"[DEBUG] LLM decision: {llm_decision}")
        current_agent = llm_decision.get('next_agent', 'end')
    return results

if __name__ == "__main__":
    initial_state = {"messages": [{"role": "user", "content": "hello"}]}
    results = run_llm_orchestrator(initial_state)
    print("LLM Orchestrator Results:")
    print(results)