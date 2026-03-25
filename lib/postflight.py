from lib.git_runner import checkout_to_branch
from lib.state_management import (
    update_last_run_for_agent,
    update_last_opened_pr_for_agent,
)


def run(repo_config, agent_name, current_commit, result) -> bool:
    """
    Handles all state updates and git recovery after an agent run attempt.
    Returns True if the runner should continue to the next agent, False to halt.
    """
    if result.status == "SUCCESS":
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SUCCESS")
        update_last_opened_pr_for_agent(
            repo_config,
            agent_name,
            current_commit,
            result.branch,
            result.pr_number,
        )
        print(f"[{agent_name}] Success — PR opened.")
        return True

    if result.status == "NO_FINDINGS":
        update_last_run_for_agent(repo_config, agent_name, current_commit, "NO_FINDINGS")
        print(f"[{agent_name}] Success — no findings.")
        return True

    # All failure cases — record state first, then attempt git recovery
    update_last_run_for_agent(
        repo_config,
        agent_name,
        current_commit,
        result.status,
        result.error,
    )
    print(f"[{agent_name}] Failed with status '{result.status}': {result.error}")

    recovered = _recover(repo_config)
    if not recovered:
        print(f"[{agent_name}] Git recovery failed — halting further agents for '{repo_config['name']}'.")
        return False

    return True


def _recover(repo_config) -> bool:
    """
    Attempts to return the repo to a clean state on the configured base branch.
    Returns True if recovery succeeded, False if it did not.
    """
    try:
        checkout_to_branch(repo_config["name"], repo_config["branch"])
        return True
    except Exception as e:
        print(f"Recovery failed for '{repo_config['name']}': {e}")
        return False
