import argparse
import sys

from lib.config_management import find_config_path, load_config, resolve_agents_on_config
from lib.state_management import get_state_with_create
from lib.repo_management import repo_exists


CONFIG_DIR = "configs"


def parse_args():
    parser = argparse.ArgumentParser(description="Review bot entry point")
    parser.add_argument("--repo", required=True, help="Repository name (must match a config filename)")
    parser.add_argument("agents", nargs="*", metavar="AGENT", help="Agent names to run (runs all configured agents if omitted)")
    return parser.parse_args()


def dispatch_agent(agent_name, agent_config, repo_config):
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

    # Repo Setup Step
    # 1) Need to check for existing state file for repo
    try:
        repo_state = get_state_with_create(config)
    except:
        print(f"Unable to get or create state file for repo {config["name"]}")
        sys.exit(f"Unable to get or create state file for repo {config["name"]}")


    # 2) Need to verify that repo exists at location in config (repo_path)
        # If not, repo needs to be cloned from github
    if not repo_exists(config["name"]):
        print(f"No local repo for {config["name"]}, cloning...")
        
    

    for agent_name, agent_config in agents:
        dispatch_agent(agent_name, agent_config, config)


if __name__ == "__main__":
    main()
