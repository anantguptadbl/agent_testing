# FixtureLibrary: Chainable test fixture builder for agent orchestration

import logging
from unittest.mock import patch, Mock
from agent_utils.remoterunnable_utils import find_all_remoterunnables
from langtest.agent_utils.models.agent_info import AgentInfo

logging.basicConfig(level=logging.DEBUG)

class FixtureLibrary:
    def __init__(self):
        
        self._input_state = None
        self._api_mocks = []
        self._agent_invocations = []
        self._agent_responses = []
        self._patchers = []
        # Load all agent info dict at initialization
        self.agent_info_dict = find_all_remoterunnables("orchestrator")
        print(f"Initialized FixtureLibrary with members: "
                      f"_input_state={self._input_state}, "
                      f"_api_mocks={self._api_mocks}, "
                      f"_agent_invocations={self._agent_invocations}, "
                      f"_agent_responses={self._agent_responses}, "
                      f"_patchers={self._patchers}, "
                      f"agent_info_dict keys={list(self.agent_info_dict.keys())}")

    def when_input_state(self, state):
        print(f"when_input_state called with state={state}")
        self._input_state = state
        print(f"_input_state set to {self._input_state}")
        return self

    def mock_api_call(self, api_path, payload, return_value):
        print(f"mock_api_call called with api_path={api_path}, payload={payload}, return_value={return_value}")
            # Special handling for requests.get
        def side_effect(url, params=None, **kwargs):
            if url == payload.get('url') and params == payload.get('params'):
                mock_response = Mock()
                mock_response.json.return_value = return_value
                return mock_response
            raise ValueError(f"Unexpected url/params: {url}, {params}")
        if api_path == "requests.get" or api_path.endswith("requests.get"):
            patcher = patch(api_path, side_effect=side_effect)
        else:
            patcher = patch(api_path, return_value=Mock(return_value=return_value))
        self._patchers.append(patcher)
        self._api_mocks.append((api_path, payload, return_value))
        print(f"_patchers updated: {self._patchers}")
        print(f"_api_mocks updated: {self._api_mocks}")
        return self

    def then_expect_agent_invocation(self, agent_name, state):
        print(f"then_expect_agent_invocation called with agent_name={agent_name}, state={state}")
        self._agent_invocations.append((agent_name, state))
        print(f"_agent_invocations updated: {self._agent_invocations}")
        return self

    def mock_agent_response(self, agent_name, response_state):
        print(f"mock_agent_response called with agent_name={agent_name}, response_state={response_state}")
        # Use agent_info_dict to infer the patch path
        agent_info: AgentInfo = self.agent_info_dict.get(agent_name)
        print(f"Retrieved agent_info for {agent_name}: {agent_info}")
        if agent_info is None:
            raise ValueError(f"Agent '{agent_name}' not found in agent_info_dict.")
        # Try to get the module path from agent_info, fallback to default if not present
        module_path = agent_info.agent_path
        patch_path = f"{module_path}.invoke"
        print(f"Determined patch_path for {agent_name}: {patch_path}")
        patcher = patch(patch_path, return_value=response_state)
        self._patchers.append(patcher)
        self._agent_responses.append((agent_name, response_state))
        print(f"_patchers updated: {self._patchers}")
        print(f"_agent_responses updated: {self._agent_responses}")
        return self

    def __enter__(self):
        print("__enter__ called. Starting all patchers.")
        self._started_patches = [p.start() for p in self._patchers]
        print(f"_started_patches: {self._started_patches}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__ called. Stopping all patchers.")
        for p in self._patchers:
            p.stop()
        print("All patchers stopped.")

    def run(self, test_func):
        print(f"run called with test_func={test_func}")
        with self:
            result = test_func(self._input_state)
        print(f"run result: {result}")
        return result

    def invoke_graph(self, graph):
        print(f"invoke_graph called with graph={graph}")
        print(f"Using _input_state: {self._input_state}")
        print("Type of input_state:", type(self._input_state))
        print("Type of graph:", type(graph))
        with self:
            result = graph.invoke(self._input_state)
        print(f"invoke_graph result: {result}")
        return result
        
    def cleanup(self):
        for patcher in self._patchers:
            patcher.stop()


    # Optionally, add more helpers for assertions or reporting as needed