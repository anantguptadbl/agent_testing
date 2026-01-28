from pydantic import BaseModel

class AgentInfo(BaseModel):
    agent_name: str
    agent_path: str
    agent_type: str
    agent_module_path: str = None

    @property
    def module_path(self):
        """Getter for agent_module_path."""
        return self.agent_path
