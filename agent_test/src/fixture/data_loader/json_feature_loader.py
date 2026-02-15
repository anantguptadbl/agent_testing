
import json
from agent_test.src.agent_utils.models.api_mock_type import APIMockType
from agent_test.src.fixture.fixture_class import FixtureLibrary

class JSONFeatureLoader():
    """Loads and parses test scenarios from JSON files."""
    def load_all(self, file_pattern):
        import glob
        all_scenarios = []
        for file in glob.glob(file_pattern):
            all_scenarios.extend(self.parse(file))
        return all_scenarios

    def parse(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def execute_scenario(self, scenario_data, run_llm_orchestrator):
        flib = FixtureLibrary(root_path=scenario_data.get("root_path", "examples.langgraph.prompt_agentic.synchronous"))
        for api_mock in scenario_data.get("mock_api_calls", []):
            flib.mock_api_call(
                api_path=api_mock["api_path"],
                payload=api_mock["payload"],
                return_value=api_mock["return_value"],
                api_type=getattr(APIMockType, api_mock.get("api_type", "REQUESTS"))
            )
        flib.when_input_state(scenario_data["input_state"])
        for agent_resp in scenario_data.get("agent_responses", []):
            flib.mock_agent_response(agent_resp["agent_name"], agent_resp["response_state"])
        flib.invoke_function(run_llm_orchestrator)
        for expect in scenario_data.get("expect_agent_invocations", []):
            flib.expect_agent_invocation(
                expect["agent_name"],
                expect["state"],
                expect.get("agent_type", "invoke"),
                expect.get("ntimes", 1)
            )
