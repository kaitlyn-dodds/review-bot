from github import Github
from github import Auth
import os
from lib.errors import GithubRepoError

_client = None

def get_client():
    global _client
    if _client is None:
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise EnvironmentError("GITHUB_TOKEN environment variable not set")
        auth = Auth.Token(github_token)
        _client = Github(auth=auth)
    return _client

def get_repo(repo_name):
    """
    Get a repo with the provided repo name
    """
    client = get_client()

    # get repo
    try:
        repo = client.get_repo(repo_name)
    except Exception as e:
        raise GithubRepoError(repo_name, reason=str(e))
    
    return repo

def open_pr(repo_config, branch_name, title, body):
    """
    Opens a new pr for the given repo on the given branch, sets 
    pr title to given tile and sets body to body argument. 

    Returns newly opened pr url and pr number
    """
    # get repo
    repo = get_repo(repo_config["github_repo"])
    
    # try to create pr
    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            base=repo_config["branch"], # branch to merge into
            head=branch_name # branch w/ changes
        )
    except Exception as e:
        raise GithubRepoError(repo_config["github_repo"], reason=str(e))
    
    return ( pr.html_url, pr.number )
    

