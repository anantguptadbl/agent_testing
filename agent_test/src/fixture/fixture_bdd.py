from pytest_bdd import given, when, then, parsers
import pytest
from agent_test.src.agent_utils.models.api_mock_type import APIMockType
from agent_test.src.fixture.fixture_class import FixtureLibrary
from examples.langgraph.prompt_agentic.synchronous.orchestrator_code import run_llm_orchestrator
import ast


@pytest.fixture
def bdd_feature_loader(request):
    # Allow passing root_path via request.param, fallback to default if not provided
    root_path = getattr(request, 'param', None)
    print(f"[DEBUG] Initializing BDD Helper with root_path: {root_path}")
    if root_path is None:
        raise ValueError("Please provide root_path as a parameter to the bdd_feature_loader fixture.")
    lib = FixtureLibrary(root_path=root_path)
    request.addfinalizer(lib.cleanup)
    return lib

@given(parsers.parse('the api_path "{api_path}" with payload \'{payload}\' is mocked to return_value \'{return_value}\''))
def mock_api_step(bdd_feature_loader, api_path, payload, return_value):
    payload_dict = ast.literal_eval(payload)
    return_value_dict = ast.literal_eval(return_value)
    bdd_feature_loader.mock_api_call(api_path, payload_dict, return_value_dict)

@given(parsers.parse("agent {agent_name} will respond with '{response}'"))
def mock_agent_response_step(bdd_feature_loader, agent_name, response):
    bdd_feature_loader.mock_agent_response(agent_name, ast.literal_eval(response))

@when(parsers.parse("the user sends '{message}' and invokes the '{orchestrator}' orchestrator"))
def send_user_message_step(bdd_feature_loader, message, orchestrator):
    bdd_feature_loader.when_input_state(ast.literal_eval(message))
    print(f"[DEBUG] Invoking orchestrator: {orchestrator} with message: {message} and type of orchestrator: {type(orchestrator)} ")
    bdd_feature_loader.invoke_function(orchestrator)

@then(parsers.parse("agent {agent_name} should be invoked with messages containing '{expected}'"))
def expect_agent_invocation_step(bdd_feature_loader, agent_name, expected):
    bdd_feature_loader.expect_agent_invocation(agent_name, ast.literal_eval(expected), "invoke", ntimes=1)

# sys.modules["agent_test.src.fixture.fixture_bdd"] = bdd_feature_loader