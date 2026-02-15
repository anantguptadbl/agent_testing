# --- Dynamic scenario loader for JSON ---
import pytest
from unittest.mock import patch
from agent_test.src.fixture.fixture_class import scenario_feature_loader
from examples.langgraph.prompt_agentic.synchronous_other.orchestrator_code import AccountState, AgentState, get_response_from_llm


@pytest.mark.parametrize("scenario_feature_loader", ["examples.langgraph.prompt_agentic.synchronous_other"], indirect=True)
def test_orchestrator_chain(scenario_feature_loader):
    agent_state = AgentState(
        user_prompt="What is the savings account balance for userId U1 and ACC123?",
        user_id="U1",
        accounts=[AccountState(account_id="ACC123", account_type="savings")]
    )
    results = (
    scenario_feature_loader
        .when_input_state(agent_state)
        .mock_agent_response(
            "get_account_balance_api", { "user_prompt": "What is the savings account balance for userId U1 and ACC123?", "user_id": "U1", "accounts": [ { "account_id": "ACC123", "account_type": "savings", "account_balance": 1000.0, "unsettled_txns": None } ] }
        )
        .invoke_function(get_response_from_llm)
        .expect_agent_invocation(
            "get_account_balance_api",
            { "user_prompt": "What is the savings account balance for userId U1 and ACC123?", "user_id": "U1", "accounts": [ { "account_id": "ACC123", "account_type": "savings", "account_balance": None, "unsettled_txns": None } ] },
            "invoke",
            ntimes=1,
        )
    )