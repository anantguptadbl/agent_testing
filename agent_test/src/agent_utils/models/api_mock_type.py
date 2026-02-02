from enum import Enum, auto

class APIMockType(Enum):
    REQUESTS = auto()
    HTTPX = auto()
    URLLIB = auto()
    AIOHTTP = auto()
    GRPC = auto()
    WEBSOCKETS = auto()
    CUSTOM = auto()
    SDK = auto()
    DB = auto()
    MQ = auto()
    GRAPHQL = auto()
    SOAP = auto()
