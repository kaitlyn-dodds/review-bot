import os

REPO_DIR = "/app/repos"

# check for repo existence
def repo_exists(repo_name):
    """
    Checks if repo with given name exists, returns boolean
    """
    path = f"{REPO_DIR}/{repo_name}"
    return os.path.isdir(path)

# Create (clone from git) repo given repo config
def clone_repo(config):
    """
    Clones the repo per the provided config, sets repo to branch 
    indicated in the repo config. Throws exception on failure. 
    """
    pass