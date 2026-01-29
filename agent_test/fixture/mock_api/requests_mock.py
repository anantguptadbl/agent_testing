from typing import override
from unittest.mock import patch, Mock
from agent_test.agent_utils.models.api_mock_type import APIMockType
from agent_test.fixture.mock_api.base_mock import BaseAPIMock


class RequestsAPIMock(BaseAPIMock):
    def get_api_type(self):
        
        return APIMockType.REQUESTS

    """Mocking strategy for requests-based APIs."""
    @override
    def create_patcher(self, api_path, payload, return_value):
        def side_effect(url, params=None, **kwargs):
            if payload and url == payload.get("url") and params == payload.get("params"):
                mock_response = Mock()
                mock_response.json.return_value = return_value
                return mock_response
            raise ValueError(f"Unexpected url/params: {url}, {params}")

        if payload is None:
            return patch(api_path, return_value=Mock(return_value=return_value))
        else:
            return patch(api_path, side_effect=side_effect)
