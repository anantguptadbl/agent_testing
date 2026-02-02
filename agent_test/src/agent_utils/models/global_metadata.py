
from abc import abstractmethod

from agent_test.src.agent_utils.models.api_mock_type import APIMockType


class GlobalMetadata:
    _api_patcher_registry = {}

    @classmethod
    def identify_patcher_type(cls, api_type: APIMockType = APIMockType.REQUESTS):
        """
        Identify the patcher class based on the payload using the factory module.
        """
        if not cls._api_patcher_registry:
            cls._api_patcher_registry = cls._build_api_patcher_registry()
        # print(f"GlobalMetadata: identify_patcher_type called with api_type={api_type} and the registry={cls._api_patcher_registry} ")
        return cls._api_patcher_registry.get(api_type, None)
    
    def _build_api_patcher_registry():
        import importlib
        import pkgutil
        from agent_test.src.fixture.mock_api import base_mock
        from agent_test.src.fixture.mock_api.base_mock import BaseAPIMock
        import agent_test.src.fixture.mock_api

        # Dynamically import all modules in the mock_api package
        package = agent_test.src.fixture.mock_api
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if not is_pkg and not module_name.endswith("base_mock"):
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    print(f"GlobalMetadata: Failed to import {module_name}: {e}")

        # print("GlobalMetadata: Building API patcher registry...")
        # print("GlobalMetadata: Found subclasses of BaseAPIMock:", BaseAPIMock.__subclasses__())
        registry = {}
        for cls in BaseAPIMock.__subclasses__():
            # print(f"GlobalMetadata: Registering API patcher class {cls} ")
            instance = cls()
            api_type = instance.get_api_type()
            # print(f"GlobalMetadata: Identified api_type={api_type} for class {cls} ")
            if api_type:
                registry[api_type] = cls
        return registry


    def get_api_patcher_class(api_type: str):
        """
        Factory function to select the correct API patcher class based on payload.
        Default is RequestsAPIMock.
        """
        from agent_test.fixture.mock_api.base_mock import BaseAPIMock
        return BaseAPIMock._api_patcher_registry.get(api_type)