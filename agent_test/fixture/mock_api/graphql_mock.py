from unittest.mock import patch, Mock
from agent_test.fixture.mock_api.base_mock import BaseAPIMock

class GraphQLAPIMock(BaseAPIMock):
    """Mocking strategy for GraphQL clients (gql, sgqlc, etc.)."""
    def create_patcher(self, api_path, payload, return_value):
        if payload is None:
            return patch(api_path, return_value=return_value)
        def side_effect(*args, **kwargs):
            # GraphQL calls may be matched on query string
            if payload and args and args[0] == payload.get("query"):
                return return_value
            raise ValueError(f"Unexpected args: {args}, kwargs: {kwargs}")
        return patch(api_path, side_effect=side_effect)

    def get_api_type(self):
        from agent_test.agent_utils.models.api_mock_type import APIMockType
        return APIMockType.GRAPHQL
