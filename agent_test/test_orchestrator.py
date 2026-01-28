import pytest
from orchestrator.orchestrator_code import builder, build_orchestrator_graph
from agent_test.fixture_class import FixtureLibrary
from unittest.mock import patch


@pytest.fixture
def scenario(request):
    s = FixtureLibrary()
    request.addfinalizer(s.cleanup)
    return s


# @pytest.fixture
# def orchestrator_fixture():
#     # Example input state
#     input_state = {'messages': [{'role': 'user', 'content': 'hello'}]}
#     # Mock API1 call and agent responses
#     fixture = (
#         FixtureLibrary()
#         .when_input_state(input_state)
#         .mock_api_call('orchestrator.main.requests.get', {'input': 'hello'}, {'output': 'hello'})
#         .mock_agent_response('agent1', {'messages': [{'role': 'agent1', 'content': 'response1'}]})
#         .mock_agent_response('agent2', {'messages': [{'role': 'agent2', 'content': 'response2'}]})
#         .mock_agent_response('agent3', {'messages': [{'role': 'agent3', 'content': 'response3'}]})
#     )
#     return fixture


@pytest.mark.asyncio
async def test_orchestrator_chain(scenario):
    # This test assumes orchestrator_graph is synchronous for demonstration.
    # If async, use pytest-asyncio and await calls.
    graph = build_orchestrator_graph(builder)

    # with patch("orchestrator.orchestrator_code.agent1.invoke") as mock_invoke:
    #     mock_invoke.return_value = {"messages": [{"role": "agent1", "content": "mocked response"}]}
    scenario_object = (
        scenario.mock_api_call(
            "orchestrator.orchestrator_code.requests.get",
            {
                "url": "http://127.0.0.1:8004/api1/getdata1",
                "params": {"input": "hello"},
            },
            {"content": "hello"},
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
    )
    await scenario_object.ainvoke_graph(graph)
    (
        scenario_object.expect_agent_invocation(
            "agent1",
            {"messages": [{"role": "user", "content": "hello"}, {"content": "hello"}]},
            "invoke",
            ntimes=1,
        )
        .expect_agent_invocation(
            "agent2",
            {"messages": [{"role": "agent1", "content": "response1"}]},
            "ainvoke",
            ntimes=1,
        )
        .expect_agent_invocation(
            "agent3",
            {"messages": [{"role": "agent2", "content": "response2"}]},
            "batch",
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
