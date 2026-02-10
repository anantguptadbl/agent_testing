import json
import ast
import pytest
from pytest_bdd import given, when, then, parsers
from agent_test.src.agent_utils.models.api_mock_type import APIMockType
from agent_test.src.fixture.fixture_class import FixtureLibrary
from examples.langgraph.prompt_agentic.synchronous.orchestrator_code import run_llm_orchestrator
# from agent_test.src.fixture.fixture_bdd import FixtureLibraryBDD

@pytest.fixture
def bdd_helper(request):
    lib = FixtureLibrary(root_path="examples.langgraph.prompt_agentic.synchronous")
    request.addfinalizer(lib.cleanup)
    return lib

@given(parsers.parse('the api_path "{api_path}" with payload \'{payload}\' is mocked to return_value \'{return_value}\''))
def mock_api_step(bdd_helper, api_path, payload, return_value):
    payload_dict = ast.literal_eval(payload)
    return_value_dict = ast.literal_eval(return_value)
    bdd_helper.mock_api_call(api_path, payload_dict, return_value_dict)

@given(parsers.parse("agent {agent_name} will respond with '{response}'"))
def mock_agent_response_step(bdd_helper, agent_name, response):
    # bdd_helper.mock_agent_response(agent_name, {"messages": [{"role": agent_name, "content": response}]})
    bdd_helper.mock_agent_response(agent_name, ast.literal_eval(response))

@when(parsers.parse("the user sends '{message}'"))
def send_user_message_step(bdd_helper, message):
    bdd_helper.when_input_state(ast.literal_eval(message))
    bdd_helper.invoke_function(run_llm_orchestrator)

@then(parsers.parse("agent {agent_name} should be invoked with messages containing '{expected}'"))
def expect_agent_invocation_step(bdd_helper, agent_name, expected):
    bdd_helper.expect_agent_invocation(agent_name, ast.literal_eval(expected), "invoke", ntimes=1)
