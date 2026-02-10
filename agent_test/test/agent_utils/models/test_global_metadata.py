from agent_test.src.agent_utils.models.global_metadata import GlobalMetadata
from agent_test.src.agent_utils.models.api_mock_type import APIMockType

def test_identify_patcher_type_returns_none_for_unknown():
    assert GlobalMetadata.identify_patcher_type(9999) is None

def test_identify_patcher_type_default():
    # Should not raise, even if registry is empty
    result = GlobalMetadata.identify_patcher_type(APIMockType.REQUESTS)
    # Could be None or a patcher class depending on registry
    assert result is None or callable(result)
