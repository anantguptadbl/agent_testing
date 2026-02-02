import logging

class AgentTestLogger:
    _logger = None

    @staticmethod
    def get_logger(name: str = "agent_test_logger"):
        if AgentTestLogger._logger is None:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            AgentTestLogger._logger = logger
        return AgentTestLogger._logger
    
    @staticmethod
    def set_logger(logger):
        """Set a custom logger instance."""
        AgentTestLogger._logger = logger
