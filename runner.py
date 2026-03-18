import argparse
import sys

from lib.config_management import find_config_path, load_config, resolve_agents_on_config
from lib.state_management import get_state_with_create, update_last_run_for_agent
from lib.repo_management import repo_exists, clone_repo, checkout_branch
from lib.github_client import get_commit_hash


CONFIG_DIR = "configs"


def parse_args():
    parser = argparse.ArgumentParser(description="Review bot entry point")
    parser.add_argument("--repo", required=True, help="Repository name (must match a config filename)")
    parser.add_argument("agents", nargs="*", metavar="AGENT", help="Agent names to run (runs all configured agents if omitted)")
    return parser.parse_args()


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
    # Agent tasks (what every agent must perform)
    # Set repo to config["branch"]
    checkout_branch(repo_config["name"], repo_config["branch"], False)

    # Get current git hash
    current_commit = get_commit_hash(repo_config["name"])

    # Skip Agent Logic

    # No new changes since last run
    if agent_state["last_run"] and agent_state["last_run"]["commit"] == current_commit:
        print("No new changes!")
        # agent should NOT be run, but the script should check status of last_opened_pr
        verify_and_update_last_opened_pr(repo_config, agent_state)
        
        # script should then update agent_state[last_run] - SKIPPED_NO_CHANGES
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SKIPPED_NO_CHANGES")
    else: # changes have been made since last run
        # TODO: need to address issue w/ endless loop over merged bot prs
        
        # TODO: call agent here
        # should agent be responsible for committing and pushing the changes??

        # assume agent completed successfully
        # TODO: commit and push all changes 

        # TODO: open pr w/ changes 

        # TODO: update last_run
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SUCCESS")

        # TODO: update last_opened_pr
        pass


    # TODO: instantiate and run the appropriate agent class
    print(f"Dispatching agent '{agent_name}' for repo '{repo_config['name']}'")


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
