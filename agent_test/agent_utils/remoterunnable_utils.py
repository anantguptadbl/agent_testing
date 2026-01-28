import inspect
import pkgutil
import importlib
import inspect
from langserve import RemoteRunnable
from langchain_core.runnables import Runnable, RunnableLambda
from agent_utils.models.agent_info import AgentInfo

# List of supported runnable types
RUNNABLE_TYPES = [RemoteRunnable, Runnable, RunnableLambda]

def find_all_remoterunnables(package_name):
    """
    Scans the given package and returns a dict of agent_name to RemoteRunnableInfo
    for all RemoteRunnable objects found in the package and its submodules.
    """
    remoterunnables = {}
    package = importlib.import_module(package_name)
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
                    print(f"Found RemoteRunnable: {name} in module: {modname} with info: {info}")
                    remoterunnables[name] = info
        except Exception:
            pass
    return remoterunnables

def find_async_nodes_in_graph(graph):
    """Returns a list of node names that are async in the given LangGraph graph object."""
    async_nodes = []
    for node_name, node_func in getattr(graph, 'nodes', {}).items():
        if inspect.iscoroutinefunction(node_func):
            async_nodes.append(node_name)
    return async_nodes
