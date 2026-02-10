from unittest.mock import patch, Mock
from agent_test.src.fixture.mock_api.base_mock import BaseAPIMock

class UrllibAPIMock(BaseAPIMock):
    """Mocking strategy for urllib/urllib3-based APIs."""
    def create_patcher(self, api_path, payload, return_value):
        if payload is None:
            return patch(api_path, return_value=Mock(return_value=return_value))
        def side_effect(*args, **kwargs):
            # args[0] is usually the URL
            if payload and args and args[0] == payload.get("url"):
                mock_response = Mock()
                mock_response.read.return_value = return_value
                return mock_response
            raise ValueError(f"Unexpected args: {args}, kwargs: {kwargs}")
        return patch(api_path, side_effect=side_effect)

    def get_api_type(self):
        from agent_test.src.agent_utils.models.api_mock_type import APIMockType
        return APIMockType.URLLIB
