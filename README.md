
# Agent Testing Library

This repository provides a comprehensive framework for building, testing, and orchestrating agentic workflows in Python. It includes utilities, fixtures, logging, and a rich set of examples demonstrating integration with various agentic frameworks and orchestration patterns.

## Project Structure

- **agent_test/**: Core testing library for agents
	- **src/agent_utils/**: Utilities for agent orchestration and metadata
		- `remoterunnable_utils.py`, `models/agent_info.py`, `models/api_mock_type.py`, `models/global_metadata.py`
	- **common/**: Logging and shared utilities
		- `agent_test_logger.py`
	- **fixture/**: Test fixtures and API mocks
		- `fixture_class.py`, `mock_api/` (various protocol mocks)
	- **test/**: Unit tests for all modules
		- `test_remoterunnable_utils.py`, `test_agent_info.py`, `test_api_mock_type.py`, `test_global_metadata.py`, `test_agent_test_logger.py`, `test_fixture_class.py`

- **examples/**: Practical agentic workflow examples
	- **common/**: Shared example code
		- `api1/api_code.py`, `worker1/main.py`, `worker2/main.py`, `worker3/main.py`
	- **crewai/**: CrewAI orchestration example
		- `orchestrator/orchestrator_code.py`
	- **langgraph/**: LangGraph agentic workflows
		- `prompt_agentic/asynchronous/orchestrator_code.py`, `prompt_agentic/asynchronous/test_orchestrator.py`
		- `prompt_agentic/synchronous/orchestrator_code.py`, `prompt_agentic/synchronous/test_orchestrator.py`
		- `simple_graph/orchestrator_code.py`, `simple_graph/test_orchestrator.py`


## Examples Section

The `examples/` directory demonstrates how to build and orchestrate agentic workflows using different frameworks and patterns. Below are direct code snippets from key example files:

### common/api1/api_code.py
```python
def api_call(input_data):
	# Simulate API logic
	return {"result": f"Processed {input_data}"}
```

### common/worker1/main.py
```python
from common.api1.api_code import api_call

def worker1_task(data):
	response = api_call(data)
	print("Worker1 received:", response)
```

### crewai/orchestrator/orchestrator_code.py
```python
def orchestrate_agents(agent_list, task):
	results = []
	for agent in agent_list:
		result = agent.run(task)
		results.append(result)
	return results
```

### langgraph/prompt_agentic/asynchronous/orchestrator_code.py
```python
import asyncio

async def async_orchestrate(agents, task):
	tasks = [agent.run_async(task) for agent in agents]
	return await asyncio.gather(*tasks)
```

### langgraph/prompt_agentic/synchronous/orchestrator_code.py
```python
def sync_orchestrate(agents, task):
	return [agent.run(task) for agent in agents]
```

### langgraph/simple_graph/orchestrator_code.py
```python
def simple_graph_orchestrate(nodes, input_data):
	output = input_data
	for node in nodes:
		output = node.process(output)
	return output
```

## Testing

Unit tests are provided in the `agent_test/test/` directory. Run all tests with:

```bash
pytest agent_test/test
```

## Run the uvicorn code


## License

See LICENSE for details.

## Future Work

Agentic Framework Alternatives (besides langgraph):

CrewAI (multi-agent orchestration)
Autogen (Microsoft’s multi-agent framework)
LangChain (chains, agents, tools)
Haystack (for RAG and agent pipelines)
OpenAI Function Calling (tool-using agents)
Semantic Kernel (Microsoft’s orchestration)
Custom agent frameworks (your own classes)
HuggingFace Transformers Agents
LlamaIndex (for agentic workflows)
DSPy (for programmatic LLM pipelines)
PromptChainer (open-source agentic framework)
Direct function/callback-based agents

#TODO 
1) API Payload type translation from feature file