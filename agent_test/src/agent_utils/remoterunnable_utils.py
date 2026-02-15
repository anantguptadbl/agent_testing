from langchain.tools import tool as tool_decorator
import inspect
import pkgutil
import importlib
import inspect
from langserve import RemoteRunnable
from langchain_core.runnables import Runnable, RunnableLambda
from mcp import Tool
from agent_test.src.agent_utils.models.agent_info import AgentInfo

# List of supported runnable types
RUNNABLE_TYPES = [RemoteRunnable, Runnable, RunnableLambda]
TOOL_TYPES = [Tool, tool_decorator]

def find_all_tools(package_name):
    """
    Scans the given package and returns a dict of tool_name to AgentInfo
    for all @tool-decorated functions found in the package and its submodules.
    """
    tools = {}
    try:
        package = importlib.import_module(package_name)
    except Exception as e:
        print(f"find_all_tools: Could not import package '{package_name}': {e}")
        return tools
    for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(modname)
            for name, obj in inspect.getmembers(module):
                # Check for langchain.tools.tool-decorated functions
                if isinstance(obj, tuple(TOOL_TYPES)):
                    info = AgentInfo(
                        agent_name=name,
                        agent_path=f"{modname}.{name}",
                        agent_type="tool",
                        agent_module_path=modname
                    )
                    tools[name] = info
        except Exception:
            pass
    print(f"find_all_tools: Found tools: {tools}")
    return tools

def find_all_remoterunnables(package_name):
    """
    Scans the given package and returns a dict of agent_name to RemoteRunnableInfo
    for all RemoteRunnable objects found in the package and its submodules.
    """
    remoterunnables = {}
    try:
        package = importlib.import_module(package_name)
    except Exception as e:
        print(f"find_all_remoterunnables: Could not import package '{package_name}': {e}")
        return remoterunnables
    for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(modname)
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, tuple(RUNNABLE_TYPES)):
                    info = AgentInfo(
                        agent_name=name,
                        agent_path=f"{modname}.{name}",
                        agent_type=type(obj).__name__,
                        agent_module_path=modname
                    )
                    remoterunnables[name] = info
        except Exception:
            pass
    print(f"find_all_remoterunnables: Found remoterunnables: {remoterunnables}")
    return remoterunnables

def find_async_nodes_in_graph(graph):
    """Returns a list of node names that are async in the given LangGraph graph object."""
    async_nodes = []
    for node_name, node_func in getattr(graph, 'nodes', {}).items():
        if inspect.iscoroutinefunction(node_func):
            async_nodes.append(node_name)
    print(f"find_async_nodes_in_graph: Found async nodes: {async_nodes}")
    return async_nodes
