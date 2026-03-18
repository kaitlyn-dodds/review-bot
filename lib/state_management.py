import os

import yaml


# This script should expose a state_management API that will be called by the runner
# or other scripts.


STATE_DIR = "/app/state"


# Phase 1: Basic API Functionality:
# create new state file for provided repo config (returns newly created state as resource)
# get state for repo at file path (throw error if no state file exists, return state as resource)

# Phase 2:
# Note: these will all need to identify the repo they are targeting as well as the specific agent
# get state for agent (specific to repo, get the nested state obj for a specific agent)
    # create empty nested agent state if one does not exist
# Get last_run.commit for a specific agent — for the skip/stale comparison
    # create empty agent state if none exists, return None if no last_run defined
# Get last_opened_pr for a specific agent — to check PR status with GitHub
    # create empty agent state if none exists, return None if no last_opened_pr defined
# Update last_run for a specific agent after any run attempt (success, skip, or failure)
# Update last_opened_pr.status for a specific agent when staleness or merge/close is detected
# Set last_opened_pr for a specific agent after a new PR is opened
# Promote last_opened_pr → last_closed_pr  for a specific agent when a PR is resolved, and clear last_opened_pr


def state_exists(repo_name):
    """Returns True if a state file exists for the given repo."""
    path = f"{STATE_DIR}/{repo_name}.yaml"
    return os.path.isfile(path)


def create_state(repo_config):
    """
    Creates a new state file for the given repo config.
    Raises FileExistsError if a state file already exists.
    Returns the newly created state as a dict.
    """
    repo_name = repo_config["name"]
    path = f"{STATE_DIR}/{repo_name}.yaml"

    if state_exists(repo_name):
        raise FileExistsError(f"State file already exists for repo '{repo_name}': {path}")

    agents = repo_config.get("agents", {})
    state = {
        "version": 1,
        "repo": repo_name,
        "agents": {
            agent_name: {
                "last_run": None,
                "last_opened_pr": None,
                "last_closed_pr": None,
            }
            for agent_name in agents
        },
    }

    os.makedirs(STATE_DIR, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True)

    return state

