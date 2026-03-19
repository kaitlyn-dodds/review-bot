
class UnknownAgentError(Exception):
    """Raised when an agent cannot be identified in the agent registry"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        message = f"Unknown agent '{agent_name}"
        super().__init__(message)

