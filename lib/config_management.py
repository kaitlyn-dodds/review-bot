import os
import yaml
import sys

CONFIG_DIR = "configs"

def find_config_path(repo_name):
    """Returns the path to the config file for the given repo name, matched case-insensitively against filenames."""
    try:
        filenames = os.listdir(CONFIG_DIR)
    except FileNotFoundError:
        return None

    for filename in filenames:
        name, ext = os.path.splitext(filename)
        if ext == ".yaml" and name.lower() == repo_name.lower():
            return os.path.join(CONFIG_DIR, filename)

    return None

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def resolve_agents_on_config(config, requested_agents):
    """
    Returns a list of (agent_name, agent_config) tuples to dispatch.
    If agent names are provided, validates each exists in the config and returns those agents.
    If none are provided, returns all agents defined in the config.
    Fails loudly if any requested agent is missing or no agents are configured.
    """
    configured_agents = config.get("agents", {})

    if requested_agents:
        missing = [a for a in requested_agents if a not in configured_agents]
        if missing:
            sys.exit(f"Error: the following agents are not defined in the '{config['name']}' config: {missing}. "
                     f"Available agents: {list(configured_agents.keys())}")
        return [(name, configured_agents[name]) for name in requested_agents]

    if not configured_agents:
        sys.exit("Error: no agents are configured for this repo.")

    return list(configured_agents.items())
