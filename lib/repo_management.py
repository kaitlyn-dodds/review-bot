import os

from lib.git_runner import clone, checkout_to_branch
from lib.errors import RepoNotFoundError

REPO_DIR = "/app/repos"


def repo_exists(repo_name):
    """
    Checks if repo with given name exists, returns boolean
    """
    path = f"{REPO_DIR}/{repo_name}"
    return os.path.isdir(path)


def clone_repo(config):
    """
    Clones the repo per the provided config, sets repo to branch
    indicated in the repo config. Raises GitCloneError on clone failure.
    Raises GitCheckoutBranchError if the initial branch checkout fails.
    """
    if repo_exists(config["name"]):
        return

    clone(config["name"], config["github_repo"])
    checkout_branch(config["name"], config["branch"])


def checkout_branch(repo_name, branch, create_branch=False):
    """
    Attempts to checkout to given branch for given repo. Optional
    create_branch boolean will attempt to create new branch when
    set to True. Raises RepoNotFoundError if the local repo doesn't exist.
    Raises GitCheckoutBranchError if the checkout fails.
    """
    if not repo_exists(repo_name):
        raise RepoNotFoundError(repo_name)

    checkout_to_branch(repo_name, branch, create_branch)
