from unittest.mock import patch, AsyncMock
from agent_test.src.fixture.mock_api.base_mock import BaseAPIMock

class AiohttpAPIMock(BaseAPIMock):
    """Mocking strategy for aiohttp-based APIs (async)."""
    def create_patcher(self, api_path, payload, return_value):
        if payload is None:
            return patch(api_path, new_callable=AsyncMock, return_value=return_value)
        async def side_effect(*args, **kwargs):
            if payload and args and args[0] == payload.get("url"):
                return return_value
            raise ValueError(f"Unexpected args: {args}, kwargs: {kwargs}")
        return patch(api_path, new_callable=AsyncMock, side_effect=side_effect)

    def get_api_type(self):
        from agent_test.src.agent_utils.models.api_mock_type import APIMockType
        return APIMockType.AIOHTTP
