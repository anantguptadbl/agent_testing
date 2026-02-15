# --- Dynamic scenario loader for JSON ---
import glob
import pytest
import agent_test.src.fixture.fixture_bdd  # Ensures step definitions are registered
from agent_test.src.agent_utils.models.api_mock_type import APIMockType
from agent_test.src.fixture.fixture_class import FixtureLibrary
from unittest.mock import patch
from pytest_bdd import scenarios
from agent_test.src.fixture.fixture_class import scenario_feature_loader
from agent_test.src.fixture.fixture_bdd import bdd_feature_loader   
from agent_test.src.fixture.data_loader.feature_loader import file_feature_loader
from examples.langgraph.prompt_agentic.synchronous.orchestrator_code import run_llm_orchestrator

@pytest.mark.parametrize("scenario_feature_loader", ["examples.langgraph.prompt_agentic.synchronous"], indirect=True)
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


# BDD test function (pytest-bdd will discover and run this via the feature file)


@pytest.mark.parametrize(
    "feature_file,root_dir",
    [("orchestrator_chain.feature", "examples/langgraph/prompt_agentic/synchronous")],
)
@pytest.mark.parametrize("bdd_feature_loader", ["examples.langgraph.prompt_agentic.synchronous"], indirect=True)
def test_orchestrator_chain_bdd(bdd_feature_loader, feature_file, root_dir):
    scenarios(feature_file)
    pass


# --- Dynamic scenario loader config ---
@pytest.mark.usefixtures("file_feature_loader")
@pytest.mark.parametrize(
    "file_feature_loader",
    [{
        "loader_type": "json",
        "root_path": "examples.langgraph.prompt_agentic.synchronous",
        "file_list": glob.glob("examples/langgraph/prompt_agentic/synchronous/test_scenarios*.json")
    }],
    indirect=True
)
def test_dynamic_feature_loader(file_feature_loader):
    pass