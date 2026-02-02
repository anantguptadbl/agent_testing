from abc import ABC, abstractmethod

class BaseAPIMock(ABC):
    
    @abstractmethod
    def create_patcher(self, api_path, payload, return_value):
        """
        Return a patcher object for the given API path, payload, and return value.
        """
        pass

    @abstractmethod
    def get_api_type(self):
        """
        Return the API mock type.
        """
        pass

    # @staticmethod
    # def identify_patcher_type(api_type: str = "requests"):
    #     """
    #     Identify the patcher class based on the payload using the factory module.
    #     """
    #     if BaseAPIMock._api_patcher_registry is None:
    #         BaseAPIMock._api_patcher_registry = build_api_patcher_registry()
    #     return BaseAPIMock._api_patcher_registry.get(api_type, None)