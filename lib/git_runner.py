import os
import subprocess

from lib.errors import GitCommitError, GitCheckoutBranchError, GitCloneError

REPO_DIR = "/app/repos"


def _repo_dir(repo_name):
    return f"{REPO_DIR}/{repo_name}"


def clone(repo_name, github_repo):
    """
    Clones the given repo into REPO_DIR via SSH.
    github_repo should be in the form 'owner/repo-name' (from config).
    Errors from the subprocess are allowed to bubble up.
    """
    ssh_url = f"git@github.com:{github_repo}.git"
    try:
        subprocess.run(["git", "clone", ssh_url, _repo_dir(repo_name)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise GitCloneError(github_repo, e.stderr)



def checkout_to_branch(repo_name, branch, new_branch=False):
    """
    Attempts to checkout to given branch for given repo. Optional
    new_branch boolean will attempt to create new branch when
    set to True.
    """
    repo_dir = _repo_dir(repo_name)
    try:
        subprocess.run(["git", "-C", repo_dir, "fetch"], check=True, capture_output=True, text=True)
        if new_branch:
            create_branch(repo_name, branch)
        else:
            subprocess.run(["git", "-C", repo_dir, "checkout", branch], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", repo_dir, "pull"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise GitCheckoutBranchError(branch, e.stderr)


def create_branch(repo_name, branch):
    """
    Creates new branch, pushes to remote origin
    """
    repo_dir = _repo_dir(repo_name)
    try:
        subprocess.run(["git", "-C", repo_dir, "checkout", "-b", branch], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", repo_dir, "push", "origin", branch], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise GitCheckoutBranchError(branch, e.stderr)


def get_current_branch(repo_name):
    """
    Returns the current git branch name.
    """
    result = subprocess.run(["git", "-C", _repo_dir(repo_name), "rev-parse", "--abbrev-ref", "HEAD"], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def discard_changes(repo_name):
    """
    Discards all staged and unstaged changes and removes untracked files.
    Raises GitCheckoutBranchError if either operation fails.
    """
    repo_dir = _repo_dir(repo_name)
    try:
        subprocess.run(["git", "-C", repo_dir, "reset", "--hard", "HEAD"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", repo_dir, "clean", "-fd"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise GitCheckoutBranchError(repo_name, e.stderr)


def delete_branch(repo_name, branch):
    """
    Deletes the given branch locally and remotely where possible.
    Local deletion is attempted first. Remote deletion is best-effort —
    failure is logged but not raised, since the branch may never have been pushed.
    """
    repo_dir = _repo_dir(repo_name)
    subprocess.run(["git", "-C", repo_dir, "branch", "-D", branch], check=True, capture_output=True, text=True)
    try:
        subprocess.run(["git", "-C", repo_dir, "push", "origin", "--delete", branch], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: could not delete remote branch '{branch}': {e.stderr.strip()}")


def get_commit_hash(repo_name):
    """
    Returns the current git commit hash (git rev-parse HEAD)
    """
    result = subprocess.run(["git", "-C", _repo_dir(repo_name), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def commit_file(repo_name, file_path, commit_msg):
    """
    Runs git command to commit the given file at the given file path.
    file_path may be absolute (including the repo dir) or relative to the repo.
    Raises GitCommitError if the file doesn't exist or the commit fails.
    """
    repo_dir = _repo_dir(repo_name)

    if not os.path.isfile(file_path):
        raise GitCommitError(file_path, "file does not exist")

    try:
        subprocess.run(
            ["git", "-C", repo_dir, "add", file_path],
            check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "-C", repo_dir, "commit", "-m", commit_msg],
            check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "-C", repo_dir, "push", "--set-upstream", "origin", "HEAD"],
            check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        raise GitCommitError(file_path, e.stderr)
