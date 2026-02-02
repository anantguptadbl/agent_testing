# agent_testing
Simple Library for testing your agents

1) API Trigger Alternatives (besides requests):

httpx (async and sync HTTP client)
urllib / urllib3 (standard library HTTP)
aiohttp (async HTTP client)
grpc (gRPC protocol for microservices)
websockets (for WebSocket APIs)
custom internal APIs (e.g., direct function calls, in-memory APIs)
third-party SDKs (e.g., AWS boto3, Azure SDK, Google API client)
database clients (e.g., SQLAlchemy, MongoDB, Redis)
message queues (e.g., RabbitMQ, Kafka, Celery tasks)
GraphQL clients (e.g., gql, sgqlc)
SOAP clients (e.g., zeep)
Custom REST clients (your own classes)
2) Agentic Framework Alternatives (besides langgraph):

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