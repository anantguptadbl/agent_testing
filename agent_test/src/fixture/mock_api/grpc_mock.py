from unittest.mock import patch, Mock
from agent_test.src.fixture.mock_api.base_mock import BaseAPIMock

class GrpcAPIMock(BaseAPIMock):
    """Mocking strategy for gRPC APIs."""
    def create_patcher(self, api_path, payload, return_value):
        # gRPC methods are usually called as stubs: stub.Method(request)
        if payload is None:
            return patch(api_path, return_value=return_value)
        def side_effect(request, *args, **kwargs):
            if payload and request == payload.get("request"):
                return return_value
            raise ValueError(f"Unexpected request: {request}")
        return patch(api_path, side_effect=side_effect)

    def get_api_type(self):
        from agent_test.src.agent_utils.models.api_mock_type import APIMockType
        return APIMockType.GRPC
