from agent_test.src.agent_utils.models.api_mock_type import APIMockType

def test_api_mock_type_enum():
    assert APIMockType.REQUESTS.name == "REQUESTS"
    assert isinstance(APIMockType.HTTPX.value, int)
    assert APIMockType.GRAPHQL in APIMockType
