from unittest.mock import patch, Mock
from agent_test.src.fixture.mock_api.base_mock import BaseAPIMock

class MQAPIMock(BaseAPIMock):
    """Mocking strategy for message queues (RabbitMQ, Kafka, Celery, etc.)."""
    def create_patcher(self, api_path, payload, return_value):
        if payload is None:
            return patch(api_path, return_value=return_value)
        def side_effect(*args, **kwargs):
            # MQ calls may be matched on message or method
            if payload and args == payload.get("args", ()) and kwargs == payload.get("kwargs", {}):
                return return_value
            raise ValueError(f"Unexpected args: {args}, kwargs: {kwargs}")
        return patch(api_path, side_effect=side_effect)

    def get_api_type(self):
        from agent_test.src.agent_utils.models.api_mock_type import APIMockType
        return APIMockType.MQ
