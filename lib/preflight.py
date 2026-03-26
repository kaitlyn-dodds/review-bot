import logging

from lib.repo_management import checkout_branch

from lib.github_client import get_pull_request
from lib.state_management import (
    get_state_for_agent,
    get_last_opened_pr_for_agent,
    update_last_run_for_agent,
    update_last_opened_pr_status,
    update_last_closed_pr_for_agent,
)

logger = logging.getLogger(__name__)


def run(repo_config, agent_name, current_commit) -> tuple[bool, str]:
    checkout_branch(repo_config["name"], repo_config["branch"])

    _verify_and_update_last_opened_pr(repo_config, agent_name)

    agent_state = get_state_for_agent(repo_config, agent_name)

    last_commit = (agent_state.get("last_run") or {}).get("commit")
    if last_commit == current_commit:
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SKIPPED_NO_CHANGES")
        return False, "no new commits since last run"

    if (agent_state.get("last_opened_pr") or {}).get("status") in ("OPEN", "STALE"):
        update_last_run_for_agent(repo_config, agent_name, current_commit, "SKIPPED_PR_OPEN")
        return False, "PR still open"

    return True, "clear to run"


def _verify_and_update_last_opened_pr(repo_config, agent_name):
    last_opened_state = get_last_opened_pr_for_agent(repo_config, agent_name)
    if not last_opened_state:
        return

    last_pr = get_pull_request(repo_config, last_opened_state["number"])

    if last_pr.state.lower() == "open":
        update_last_opened_pr_status(repo_config, agent_name, "STALE")

    elif last_pr.state.lower() == "closed" and not last_pr.merged:
        update_last_opened_pr_status(repo_config, agent_name, "CLOSED_WITHOUT_MERGE")
        update_last_closed_pr_for_agent(
            repo_config,
            agent_name,
            {
                "pr_number": last_opened_state["number"],
                "branch": last_opened_state["branch"],
                "opened_date": last_opened_state["opened_date"],
                "closed_date": last_pr.closed_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "CLOSED_WITHOUT_MERGE"
        )

    elif last_pr.state.lower() == "closed" and last_pr.merged:
        update_last_opened_pr_status(repo_config, agent_name, "MERGED")
        update_last_closed_pr_for_agent(
            repo_config,
            agent_name,
            {
                "pr_number": last_opened_state["number"],
                "branch": last_opened_state["branch"],
                "opened_date": last_opened_state["opened_date"],
                "closed_date": last_pr.closed_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )

    else:
        logger.warning(f"Last opened PR #{last_opened_state['number']} is in an unknown state")
