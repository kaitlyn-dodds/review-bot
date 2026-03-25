import argparse
import sys

from lib.config_management import find_config_path, load_config, resolve_agents_on_config
from lib.state_management import get_state_with_create
from lib.repo_management import repo_exists, clone_repo
from lib.agent_lifecycle import dispatch


CONFIG_DIR = "configs"


def parse_args():
    parser = argparse.ArgumentParser(description="Review bot entry point")
    parser.add_argument("--repo", required=True, help="Repository name (must match a config filename)")
    parser.add_argument("agents", nargs="*", metavar="AGENT", help="Agent names to run (runs all configured agents if omitted)")
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.repo:
        sys.exit("No repo name provided, exiting runner")

    config_path = find_config_path(args.repo)
    if config_path is None:
        sys.exit(f"Error: no config file found for repo '{args.repo}' in '{CONFIG_DIR}/'.")

    config = load_config(config_path)
    agents = resolve_agents_on_config(config, args.agents)

    try:
        repo_state = get_state_with_create(config)
    except:
        print(f"Unable to get or create state file for repo {config['name']}")
        sys.exit(f"Unable to get or create state file for repo {config['name']}")

    if not repo_exists(config["name"]):
        print(f"No local repo for {config['name']}, cloning...")
        clone_repo(config)

    for agent_name, agent_config in agents:
        should_continue = dispatch(agent_name, config, agent_config, repo_state["agents"][agent_name])
        if not should_continue:
            print(f"Halting remaining agents for '{config['name']}' due to unrecoverable failure.")
            break


if __name__ == "__main__":
    main()
