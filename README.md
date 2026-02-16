<p align="center">
  <img src="agentic_testing.png" alt="agent-testing logo" width="180"/>
</p>

# Bridging the Gap: Effortless Testing for Agentic Frameworks with `agent-testing`

## Introduction

Agentic frameworks like LangChain, LangGraph, CrewAI, and AutoGen are revolutionizing how we build intelligent, event-driven systems. But when it comes to testing these agents, most developers hit a wall. Traditional testing tools are cumbersome, verbose, and ill-suited for the dynamic, stateful, and event-driven nature of agentic workflows.

In this article, I’ll show you why current approaches fall short, and how the `agent-testing` library makes agent testing as seamless and expressive as the frameworks themselves.

---

## The Testing Gap: Why Existing Tools Struggle

Most agentic systems are tested using generic tools like `pytest` or `unittest`, often with a tangle of manual mocks and fixtures. This leads to several pain points:

- **Complexity:** Simulating multi-agent interactions is verbose and error-prone.
- **Poor Coverage:** Hard to express event-driven flows and state transitions.
- **Lack of Scenarios:** No easy way to parameterize or reuse real-world agent scenarios.

**Example: Traditional Test**

```python
def test_agent_response():
    agent = MyAgent()
    response = agent.act({"input": "hello"})
    assert response == "expected"
# No orchestration, no event simulation, no scenario coverage
```

This approach doesn’t scale for orchestrators, toolchains, or multi-agent systems.

---

## Agentic Frameworks = Event-Driven Architectures

Agentic systems are fundamentally event-driven:
- Agents receive messages, update state, and trigger tools.
- The orchestration is dynamic, with state and events flowing between components.

**Testing should reflect this!** We need tools that can simulate, validate, and assert on these flows—not just static input/output.

---

## Introducing `agent-testing`

The `agent-testing` library is designed for agentic frameworks. It provides three expressive ways to write tests:

### How to install
To install the latest release from PyPI:

```bash
pip install agentic-testing
```

To install with optional dependencies for LangGraph or CrewAI support:

```bash
pip install agentic-testing[langgraph]
# or
pip install agentic-testing[crewai]
```

To install directly from the repository (latest main branch):

```bash
pip install git+https://github.com/anantguptadbl/agent_testing.git
```

> **Note:** Requires Python 3.13 or newer.

---

### Orchestrator Code

Below is a simplified version of the orchestrator code used for agentic workflow testing (from `examples/langgraph/prompt_agentic/synchronous/orchestrator_code.py`).

```python
from typing import TypedDict
import uuid
from langserve import RemoteRunnable
import openai
import requests

class AgentState(TypedDict):
    messages: list[dict]

# Initialize connections to the agents
agent1 = RemoteRunnable("http://localhost:8001/agent1/process")
agent2 = RemoteRunnable("http://localhost:8002/agent2/process")
agent3 = RemoteRunnable("http://localhost:8003/agent3/process")
agent4 = RemoteRunnable("http://localhost:8003/agent4/process")
agent5 = RemoteRunnable("http://localhost:8003/agent5/process")

def call_api1(state):
    url = "http://127.0.0.1:8004/api1/getdata1"
    params = {"input": "hello"}
    response = requests.post(url, params=params)
    state["messages"].append(response.json())
    return state

def call_a1(state):
    if state["messages"][-1]["content"] == "hello":
        result = agent1.invoke(state)
        return result
    return state

def call_a2(state):
    result = agent2.invoke(state)
    return result

def call_a3(state):
    already_processed = any(
        msg.get("content") == "Processed by agent3" for msg in state["messages"]
    )
    if not already_processed:
        result = agent3.invoke(state)
        result["messages"].append({"role": "system", "content": "Processed by agent3", "uuid": uuid.uuid4().hex})
    return result

def call_a4(state):
    result = agent4.batch(state)
    result["messages"].append({"role": "system", "content": "Processed by agent4", "uuid": uuid.uuid4().hex})
    return result

def call_a5(state):
    result = agent5.batch(state)
    return result

openai.api_key = ""  # Set your OpenAI API key

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
    You are an orchestrator for agentic workflows. Generate the next_agent name.
    The order of agent execution is api1 -> a1 -> a2 -> a3 -> end
    If the history shows only user and api1, output a1
    If a1 has completed, output a2
    If a1 and a2 have completed, output a3
    If a1, a2, a3 have completed, output end
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
    current_agent = "api1"
    while current_agent != "end":
        agent_func = AGENT_FUNCTIONS.get(current_agent)
        if agent_func is None:
            break
        result = agent_func(state)
        results[current_agent] = result
        history.append({"agent": current_agent, "result": result})
        state = result if isinstance(result, dict) else state
        llm_decision = query_llm_for_next_agent(state, history)
        current_agent = llm_decision.get('next_agent', 'end')
    return results
```
```
This orchestrator demonstrates how agentic workflows can be coordinated, with each agent invoked in sequence and the next step determined by an LLM. This code is used as the basis for the fixture, BDD, and JSON scenario tests described above.
```

### 1. Scenario Based Testing

Use Python fixtures to set up agent state, mock API calls, and validate agent/tool invocations. This approach is powerful for granular, reusable test setups.

```python
def test_orchestrator_chain(scenario_feature_loader):
    (
    scenario_feature_loader.mock_api_call(
            api_path="orchestrator_code.requests.post",
            payload=
            {
                "url": "http://127.0.0.1:8004/api1/getdata1",
                "params": {"input": "hello"},
            },
            return_value={"content": "hello"},
            api_type=APIMockType.REQUESTS
        )
        .when_input_state({"messages": [{"role": "user", "content": "hello"}]})
        .mock_agent_response(
            "agent1", {"messages": [{"role": "agent1", "content": "response1"}]}
        )
        .mock_agent_response(
            "agent2", {"messages": [{"role": "agent2", "content": "response2"}]}
        )
        .mock_agent_response(
            "agent3", {"messages": [{"role": "agent3", "content": "response3"}]}
        )
        .invoke_function(run_llm_orchestrator)
        .expect_agent_invocation(
            "agent1",
           {'messages': [{'role': 'user', 'content': 'hello'}, {'content': 'hello'}]},
            "invoke",
            ntimes=1,
        )
        .expect_agent_invocation(
            "agent2",
            {'messages': [{'role': 'agent1', 'content': 'response1'}]},
            "invoke",
            ntimes=1,
        )
        .expect_agent_invocation(
            "agent3",
            {'messages': [{'role': 'agent2', 'content': 'response2'}]},
            "invoke",
            ntimes=1,
        )
    )
    # Add more assertions as needed
```

#### Detailed Explanation of Fixture-Based Testing Steps

- **when_input_state**: This fixture method sets up the initial state for the orchestrator or agent. It simulates the starting context, such as the initial messages or environment the agent will see. For example, `.when_input_state({"messages": [{"role": "user", "content": "hello"}]})` ensures the orchestrator starts with a user message "hello" in its state. This is crucial for reproducible, scenario-driven tests.

- **mock_api_call**: This fixture mocks external API calls made by the orchestrator or agents. It intercepts calls (e.g., HTTP requests) and returns predefined responses, allowing you to simulate API behavior without making real network calls. The parameters include:
  - `api_path`: The import path to the function being mocked (e.g., `orchestrator_code.requests.post`).
  - `payload`: The expected arguments for the API call (e.g., URL and params).
  - `return_value`: The mock response to return (e.g., `{ "content": "hello" }`).
  - `api_type`: The type of API being mocked (e.g., `APIMockType.REQUESTS`).
  This enables deterministic, isolated tests regardless of external service availability.

- **mock_agent_response**: This fixture simulates the response of a specific agent when invoked by the orchestrator. For example, `.mock_agent_response("agent1", {"messages": [{"role": "agent1", "content": "response1"}]})` ensures that when the orchestrator calls agent1, it receives the specified response. This is essential for testing orchestrator logic without running real agent servers.

- **invoke_function**: This step triggers the actual function under test—in this case, the orchestrator logic (e.g., `run_llm_orchestrator`). It runs the orchestrator with the prepared state and mocks, simulating a real workflow execution.

- **expect_agent_invocation**: This assertion checks that a particular agent was called with the expected input and the correct method (e.g., `invoke`), and optionally how many times (`ntimes`). For example, `.expect_agent_invocation("agent1", {...}, "invoke", ntimes=1)` asserts that agent1 was invoked once with the specified state. This validates that the orchestrator is coordinating agents as intended.

These fixtures and assertions together enable expressive, scenario-driven, and fully controlled tests for complex agentic workflows.

---

### 2. Feature File (BDD) Testing

Write Gherkin-style feature files for scenario-driven tests. Use `pytest-bdd` to discover and run these scenarios.

**Feature File Example:**

```gherkin
Feature: Orchestrator Chain
  Scenario: User sends hello
    Given the user sends "hello"
    When the orchestrator runs
    Then agent1 should respond with "response1"
```

**Test Runner:**

```python
@pytest.mark.parametrize("feature_file,root_dir", [("orchestrator_chain.feature", "examples/langgraph/prompt_agentic/synchronous")])
@pytest.mark.parametrize("bdd_feature_loader", ["examples.langgraph.prompt_agentic.synchronous"], indirect=True)
def test_orchestrator_chain_bdd(bdd_feature_loader, feature_file, root_dir):
    scenarios(feature_file)
```

---

### 3. JSON Scenario Testing

Define test scenarios in JSON for easy parameterization and automation. Load scenarios dynamically and run tests with minimal code.

```python
@pytest.mark.usefixtures("file_feature_loader")
@pytest.mark.parametrize(
    "file_feature_loader",
    [{
        "loader_type": "json",
        "root_path": "examples/langgraph/prompt_agentic/synchronous",
        "file_list": glob.glob("examples/langgraph/prompt_agentic/synchronous/test_scenarios*.json")
    }],
    indirect=True
)
def test_dynamic_feature_loader(file_feature_loader):
    pass
```

---

## Deep Dive: Testing a LangGraph Orchestrator

Let’s break down the structure of a real-world agentic test suite, using `langgraph/prompt_agentic/synchronous/*.py` as an example.

### The Orchestrator

- Implements the agent orchestration logic.
- Uses `@tool` decorators and `bind_tools` for tool registration.
- Handles state updates and tool invocation loop.

### The Test Cases

- **Fixture Tests:** Set up agent state, mock responses, and validate orchestration.
- **BDD Tests:** Use feature files for scenario-driven validation.
- **JSON Tests:** Parameterize and automate scenario coverage.

This modular approach means you can test complex, event-driven agent flows with concise, readable code.




## More Examples

#### Agent-Testing Example Gallery

Explore a variety of agentic testing examples in the [agent_testing repository](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph):

1. **LangGraph Prompt Agentic Asynchronous**
   - [View Example](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph/prompt_agentic/asynchronous)
   - Demonstrates asynchronous orchestration of agents using LangGraph. Includes tests for event-driven flows where agent responses and state updates occur out of order, simulating real-world async interactions.

2. **LangGraph Prompt Agentic Synchronous**
   - [View Example](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph/prompt_agentic/synchronous)
   - Shows synchronous agent orchestration, where agents are invoked in a strict sequence. Features fixture, BDD, and JSON scenario tests for validating stepwise agent flows.

3. **LangGraph Prompt Agentic Tool-Based Invocation**
   - [View Example](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph/prompt_agentic/synchronous_other)
   - Focuses on tool-based agent invocation, testing how orchestrators bind and trigger tools dynamically. Useful for scenarios where agents leverage external tools or APIs.

4. **LangGraph Simple Graph Asynchronous**
   - [View Example](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph/simple_graph/asynchronous)
   - Illustrates a minimal asynchronous agent graph. Tests cover parallel agent execution and state merging, ideal for distributed or concurrent agentic workflows.

5. **LangGraph Simple Graph Synchronous**
   - [View Example](https://github.com/anantguptadbl/agent_testing/tree/main/examples/langgraph/simple_graph/synchronous)
   - Provides a basic synchronous agent graph. Includes tests for linear agent chains and deterministic state transitions, suitable for simple orchestrations.

Each example contains orchestrator code, test cases, and scenario files to help you understand and adapt agentic testing patterns for your own projects.


## Future Work

- Expand support for more agentic frameworks.
- Add coverage for asynchronous and distributed agents.
- Integrate with CI/CD for automated scenario validation.
- Provide richer reporting and debugging tools.

---

## Conclusion

`agent-testing` brings agentic system testing up to the level of the frameworks themselves. Whether you prefer fixtures, feature files, or JSON, you can test complex agent flows with ease and clarity.

**Ready to make your agent tests as smart as your agents? Try `agent-testing` today!**

---

Let me know if you want more code samples or a deeper dive into any section!
