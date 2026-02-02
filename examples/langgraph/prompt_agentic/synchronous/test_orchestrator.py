import pytest
from agent_test.src.agent_utils.models.api_mock_type import APIMockType
from agent_test.src.fixture.fixture_class import FixtureLibrary
from unittest.mock import patch
from examples.langgraph.prompt_agentic.synchronous.orchestrator_code import run_llm_orchestrator


@pytest.fixture
def scenario(request):
    s = FixtureLibrary(root_path="examples.langgraph.prompt_agentic.synchronous")
    request.addfinalizer(s.cleanup)
    return s

def test_orchestrator_chain(scenario):
    (
    scenario.mock_api_call(
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


# def test_orchestrator_chain(scenario):
#     # This test assumes orchestrator_graph is synchronous for demonstration.
#     # If async, use pytest-asyncio and await calls.
#     graph = build_orchestrator_graph(builder)


#     # with patch("orchestrator.orchestrator_code.agent1.invoke") as mock_invoke:
#     #     mock_invoke.return_value = {"messages": [{"role": "agent1", "content": "mocked response"}]}
#     result = (
#         scenario
#         .mock_api_call(
#             "orchestrator.orchestrator_code.requests.get",
#             {
#                 "url": "http://127.0.0.1:8004/api1/getdata1",
#                 "params": {"input": "hello"},
#             },
#             {"content": "hello"},
#         )
#         .when_input_state({"messages": [{"role": "user", "content": "hello"}]})
#         .mock_agent_response('agent1', {'messages': [{'role': 'agent1', 'content': 'response1'}]})
#         .mock_agent_response('agent2', {'messages': [{'role': 'agent2', 'content': 'response2'}]})
#         .mock_agent_response('agent3', {'messages': [{'role': 'agent3', 'content': 'response3'}]})
#         .invoke_graph(graph)
#     )

#         assert "messages" in result
#         # Add more assertions as needed
