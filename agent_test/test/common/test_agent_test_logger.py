import logging
import pytest
from agent_test.src.common.agent_test_logger import AgentTestLogger

def test_get_logger_is_singleton():
    logger1 = AgentTestLogger.get_logger("test_logger")
    logger2 = AgentTestLogger.get_logger("test_logger")
    assert logger1 is logger2

def test_set_logger_sets_custom_logger():
    custom_logger = logging.getLogger("custom_logger")
    AgentTestLogger.set_logger(custom_logger)
    assert AgentTestLogger.get_logger() is custom_logger
