from agent_test.src.agent_utils.models.agent_info import AgentInfo

def test_agent_info_fields():
    info = AgentInfo(agent_name="a", agent_path="b", agent_type="c", agent_module_path="d")
    assert info.agent_name == "a"
    assert info.agent_path == "b"
    assert info.agent_type == "c"
    assert info.agent_module_path == "d"

def test_agent_info_module_path_property():
    info = AgentInfo(agent_name="a", agent_path="b", agent_type="c")
    assert info.module_path == "b"
