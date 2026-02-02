import pytest
from agent_test.src.fixture.fixture_class import FixtureLibrary

def test_fixturelibrary_initialization():
    fixture = FixtureLibrary(root_path="orchestrator")
    assert hasattr(fixture, "_input_state")
    assert hasattr(fixture, "_api_mocks")
    assert hasattr(fixture, "_patchers")
    assert isinstance(fixture.results, list)

def test_when_input_state_sets_state():
    fixture = FixtureLibrary(root_path="orchestrator")
    fixture.when_input_state({"foo": "bar"})
    assert fixture._input_state == {"foo": "bar"}
