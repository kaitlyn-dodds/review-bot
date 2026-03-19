import argparse
import sys

# Libraries
from lib.config_management import find_config_path, load_config, resolve_agents_on_config
from lib.state_management import get_state_with_create, update_last_run_for_agent, get_state_for_agent, update_last_opened_pr_for_agent
from lib.repo_management import repo_exists, clone_repo, checkout_branch
from lib.git_runner import get_commit_hash
from lib.errors import UnknownAgentError

# Agents
from agents.issue_scanner import IssueScannerAgent


CONFIG_DIR = "configs"

AGENT_REGISTRY = {
    "issue_scanner": IssueScannerAgent,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Review bot entry point")
    parser.add_argument("--repo", required=True, help="Repository name (must match a config filename)")
    parser.add_argument("agents", nargs="*", metavar="AGENT", help="Agent names to run (runs all configured agents if omitted)")
    return parser.parse_args()


def run_agent(agent_name, repo_config, agent_config, agent_state):
    """Instantiates and runs the appropriate agent class."""
    agent_class = AGENT_REGISTRY.get(agent_name)
    if agent_class is None:
        print(f"Unknown agent '{agent_name}', skipping.")
        raise UnknownAgentError(agent_name)

    agent = agent_class(repo_config, agent_config, agent_state)
    return agent.run()  # agent owns: reading files, calling Claude, creating branch, opening PR


def verify_and_update_last_opened_pr(repo_config, agent_state):
    # if no last opened, do nothing
    # check status of last opened pr in github (merged?)
    # if no changes (e.g. still open)
        # TODO: figure out staleness logic, for now just return
    # if closed, figure out reason (e.g. merged, closed w/out merge?)
    # update state on last_opened_pr
    # update state on last_closed_pr to reflect this pr 
    pass


def dispatch_agent(agent_name, repo_config, agent_config, agent_state):
    checkout_branch(repo_config["name"], repo_config["branch"], False)
    current_commit = get_commit_hash(repo_config["name"])

    # Need to do this step regardless of if additional changes have been made
    verify_and_update_last_opened_pr(repo_config, agent_state)

    # get refreshed state
    agent_state = get_state_for_agent(repo_config, agent_name)

    # TODO: commit will change if last pr merged, need to workout this endless loop... 
    # Skip if nothing new
    last_commit = agent_state.get("last_run") or {}.get("commit")
    if last_commit == current_commit:
        print(f"[{agent_name}] No new commits since last run, skipping.")
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SKIPPED_NO_CHANGES")
        return

    # Skip if a bot PR is still open — don't pile on
    if agent_state.get("last_opened_pr") or {}.get("status") == "open":
        print(f"[{agent_name}] PR still open, skipping.")
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SKIPPED_PR_OPEN")
        return

    # Run the agent
    try:
        print(f"[{agent_name}] Running against commit {current_commit[:7]}...")
        result = run_agent(agent_name, repo_config, agent_config, agent_state)
    except UnknownAgentError as error:
        update_last_run_for_agent(
            repo_config, 
            agent_name, 
            current_commit, 
            "FAILED_WITH_ERROR", 
            str(error)
        )
        return

    # if result suceeded and pr was opened
    if result and result.get("pr_url"):
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SUCCESS")
        update_last_opened_pr_for_agent(repo_config, agent_name, result)
        return 
    
    # no new pr 
    update_last_run_for_agent(repo_config, agent_name, current_commit, "NO_FINDINGS")


def main():
    args = parse_args()

    if not args.repo:
        sys.exit(f"No repo name provided, exiting runner")

    config_path = find_config_path(args.repo)
    if config_path is None:
        sys.exit(f"Error: no config file found for repo '{args.repo}' in '{CONFIG_DIR}/'.")

    config = load_config(config_path)
    agents = resolve_agents_on_config(config, args.agents)

    # 1) Check for existing state file for repo
    try:
        repo_state = get_state_with_create(config)
    except:
        print(f"Unable to get or create state file for repo {config["name"]}")
        sys.exit(f"Unable to get or create state file for repo {config["name"]}")

    # 2) Verify that repo exists at location in config (repo_path)
    if not repo_exists(config["name"]):
        print(f"No local repo for {config["name"]}, cloning...")
        clone_repo(config)

    # 3) Run agents against repo
    for agent_name, agent_config in agents:
        dispatch_agent(agent_name, config, agent_config, repo_state["agents"][agent_name])


if __name__ == "__main__":
    main()
