import os

from lib.github_client import clone, checkout_to_branch

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
    
    if repo_exists(config["name"]):
        return # repo already exists
    
    try:
        clone(config["name"], config["github_repo"])
        checkout_branch(config["name"], config["branch"])
    except:
        print(f"Unable to clone repo {config["github_repo"]}")
        # TODO: use dedicated exception type
        raise Exception(f"Unable to clone repo {config["github_repo"]}")

def checkout_branch(repo_name, branch, create_branch=False):
    """
    Attempts to checkout to given branch for given repo. Optional 
    create_branch boolean will attempt to create new branch when 
    set to True. 
    """
    # Verify repo exists  
    if not repo_exists(repo_name):
        # TODO: use dedicated exception type
        raise Exception(f"No repo exists for {repo_name}, cannot checkout branch {branch} for nonexistent repo")

    # commit outstanding changes?
    # skip for now

    # attempt to checkout to branch
    try:
        checkout_to_branch(repo_name, branch, create_branch)
    except:
        print(f"Unable to checkout to branch {branch} for repo {repo_name}")
        # TODO: use dedicated exception type
        raise Exception(f"Unable to checkout to branch {branch} for repo {repo_name}")
        
