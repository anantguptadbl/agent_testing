# FixtureLibrary: Chainable test fixture builder for agent orchestration

import logging
from unittest.mock import AsyncMock, patch, Mock
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
        self.results = []
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
        patcher = self._create_api_patcher(api_path, payload, return_value)
        self._patchers.append((patcher, None, None))
        self._api_mocks.append((api_path, payload, return_value))
        print(f"_patchers updated: {self._patchers}")
        print(f"_api_mocks updated: {self._api_mocks}")
        return self

    def _create_api_patcher(self, api_path, payload, return_value):
        def side_effect(url, params=None, **kwargs):
            if url == payload.get("url") and params == payload.get("params"):
                mock_response = Mock()
                mock_response.json.return_value = return_value
                return mock_response
            raise ValueError(f"Unexpected url/params: {url}, {params}")

        if api_path == "requests.get" or api_path.endswith("requests.get"):
            return patch(api_path, side_effect=side_effect)
        else:
            return patch(api_path, return_value=Mock(return_value=return_value))

    def expect_agent_invocation(self, agent_name, state, agent_type="invoke", ntimes=1):
        print(
            f"Then_expect_agent_invocation called with agent_name={agent_name}, state={state}"
        )
        if (
            self.was_agent_method_called(
                agent_name, agent_type, ntimes, input_args=state
            )
            == False
        ):
            raise AssertionError(
                f"Expected agent '{agent_name}' to be invoked with state {state}, but it was not."
            )
        return self
        # self._agent_invocations.append((agent_name, state))
        # print(f"_agent_invocations updated: {self._agent_invocations}")

    def mock_agent_response(self, agent_name, response_state):
        print(
            f"mock_agent_response called with agent_name={agent_name}, response_state={response_state}"
        )
        # Use agent_info_dict to infer the patch path
        agent_info = self._get_agent_info(agent_name)
        module_path = agent_info.agent_path
        for method in ["invoke", "ainvoke", "batch"]:
            patcher = self._create_agent_patcher(module_path, method, response_state)
            self._patchers.append((patcher, agent_name, method))
        self._agent_responses.append((agent_name, response_state))
        print(f"_patchers updated: {self._patchers}")
        print(f"_agent_responses updated: {self._agent_responses}")
        return self

    def _get_agent_info(self, agent_name):
        agent_info: AgentInfo = self.agent_info_dict.get(agent_name)
        if agent_info is None:
            raise ValueError(f"Agent '{agent_name}' not found in agent_info_dict.")
        print(f"Found agent_info: {agent_info}  for agent_name: {agent_name}")
        return agent_info

    def _create_agent_patcher(self, module_path, method, response_state):
        patch_path = f"{module_path}.{method}"
        if method in ["ainvoke"]:
            # Patch async methods to return a coroutine resolved to response_state
            async_mock = AsyncMock()
            async_mock.return_value = response_state
            return patch(patch_path, new=async_mock)
        else:
            return patch(patch_path, return_value=response_state)

    def __enter__(self):
        print("__enter__ called. Starting all patchers.")
        self._started_patches = self._start_all_patchers()
        print(f"_started_patches: {self._started_patches}")
        return self

    def _start_all_patchers(self):
        return [patcher.start() for patcher, _, _ in self._patchers]

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__ called. Stopping all patchers.")
        self._stop_all_patchers
        print("All patchers stopped.")

    def _stop_all_patchers(self):
        for patcher, _, _ in self._patchers:
            patcher.stop()

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
        self.results.append(result)
        return self

    async def ainvoke_graph(self, graph):
        print(f"ainvoke_graph called with graph={graph}")
        print(f"Using _input_state: {self._input_state}")
        print("Type of input_state:", type(self._input_state))
        print("Type of graph:", type(graph))
        with self:
            result = await graph.ainvoke(self._input_state)
        print(f"ainvoke_graph result: {result}")
        self.results.append(result)
        return self

    def cleanup(self):
        self._stop_all_patchers()

    def _get_patch_index_by_agent(self, agent_name, method=None):
        """
        Returns the index of the patch for a given agent and method (e.g., 'invoke', 'ainvoke', 'batch').
        If method is None, returns all indices for the agent.
        """
        indices = []
        for i, patch_info in enumerate(self._patchers):
            # patch_info is (patcher, agent_name, method) for agent patches, or just patcher for others
            if isinstance(patch_info, tuple) and len(patch_info) == 3:
                _, patch_agent_name, patch_method = patch_info
                if patch_agent_name == agent_name:
                    if method is None or patch_method == method:
                        indices.append(i)
        return indices if method is None else (indices[0] if indices else None)

    def _was_patch_called(self, patch_index):
        """
        Returns True if the patch at patch_index was called during the test run.
        """
        if not hasattr(self, '_started_patches'):
            raise RuntimeError("Patches have not been started. Use within a context manager.")
        mock_obj = self._started_patches[patch_index]
        return getattr(mock_obj, 'called', False)

    def was_agent_method_called(self, agent_name, method, expected_count=1, input_args=None):
        """
        Asserts the patch for the given agent and method was called expected_count times.
        If input_args is provided, only counts calls with matching args.
        Returns True if assertion passes, else raises AssertionError.
        """
        print(f"was_agent_method_called called with agent_name={agent_name}, method={method}, expected_count={expected_count}, input_args={input_args}")
        print("The self._started_patches are:", self._started_patches)
        idx = self._get_patch_index_by_agent(agent_name, method)
        if idx is None:
            raise ValueError(f"No patch found for agent '{agent_name}' and method '{method}'")
        if not hasattr(self, '_started_patches'):
            raise RuntimeError("Patches have not been started. Use within a context manager.")
        mock_obj = self._started_patches[idx]
        print(f"The mock_obj for agent '{agent_name}' and method '{method}' is:", mock_obj)
        # If input_args is None, count all calls
        if input_args is None:
            call_count = mock_obj.call_count
        else:
            # Filter calls by input_args
            print(f"Counting calls with specific input_args: {input_args} and agent_name: {agent_name}, method: {method}")
            call_count = 0
            for call in getattr(mock_obj, 'call_args_list', []):
                args, kwargs = call
                print(f"The current call has args: {args}, kwargs: {kwargs}")
                if(args and len(args) == 1 and args[0] == input_args):
                    call_count += 1
        assert call_count == expected_count, (
            f"Expected {expected_count} calls to agent '{agent_name}' method '{method}', but got {call_count} (input_args={input_args})"
        )
        return True

    def was_api_patch_called(self, api_path):
        """
        Returns True if the patch for the given API path was called.
        """
        for i, patcher in enumerate(self._patchers):
            target = getattr(patcher, 'attribute', None) or getattr(patcher, 'target', None)
            if target == api_path:
                return self._was_patch_called(i)
        raise ValueError(f"No patch found for API path '{api_path}'")


    # Optionally, add more helpers for assertions or reporting as needed