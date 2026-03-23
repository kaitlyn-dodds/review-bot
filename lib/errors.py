
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

class GitCheckoutBranchError(Exception):
    """Raised when a git branch checkout or creation fails"""
    def __init__(self, branch_name, reason=None):
        self.branch_name = branch_name
        message = f"Failed to checkout branch '{branch_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class GithubRepoError(Exception):
    """Raised when error thrown interacting w/ github repo"""
    def __init__(self, repo_name, reason=None):
        self.repo_name = repo_name
        message = f"Unable to interact with repo '{repo_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


