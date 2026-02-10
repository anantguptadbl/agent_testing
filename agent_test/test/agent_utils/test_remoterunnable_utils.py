import types
import pytest
from agent_test.src.agent_utils import remoterunnable_utils

def test_find_all_remoterunnables_empty():
    # Should return empty dict for non-existent package
    result = remoterunnable_utils.find_all_remoterunnables("nonexistent_package")
    assert isinstance(result, dict)
    assert len(result) == 0

def test_find_async_nodes_in_graph():
    class DummyGraph:
        def __init__(self):
            async def async_func(): pass
            def sync_func(): pass
            self.nodes = {
                "a": async_func,
                "b": sync_func
            }
    graph = DummyGraph()
    async_nodes = remoterunnable_utils.find_async_nodes_in_graph(graph)
    assert "a" in async_nodes
    assert "b" not in async_nodes
