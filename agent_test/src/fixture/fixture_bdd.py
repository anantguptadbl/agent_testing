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