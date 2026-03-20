
class UnknownAgentError(Exception):
    """Raised when an agent cannot be identified in the agent registry"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        message = f"Unknown agent '{agent_name}"
        super().__init__(message)


class GitCommitError(Exception):
    """Raised when a git commit operation fails"""
    def __init__(self, file_path, reason=None):
        self.file_path = file_path
        message = f"Failed to commit file '{file_path}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)

