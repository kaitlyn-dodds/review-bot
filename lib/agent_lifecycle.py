import logging
from dataclasses import dataclass
from typing import Optional
import anthropic

from agents.issue_scanner import IssueScannerAgent
from lib.git_runner import get_commit_hash
from lib.errors import UnknownAgentError, GitCommitError, GithubRepoError, GitCheckoutBranchError, ClaudeMaxTokensError
import lib.preflight as preflight
import lib.postflight as postflight

logger = logging.getLogger(__name__)

AGENT_REGISTRY = {
    "issue_scanner": IssueScannerAgent,
}


@dataclass
class AgentRunResult:
    status: str
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    branch: Optional[str] = None
    error: Optional[str] = None


def dispatch(agent_name, repo_config, agent_config, agent_state) -> bool:
    current_commit = get_commit_hash(repo_config["name"])

    should_run, reason = preflight.run(repo_config, agent_name, current_commit)
    if not should_run:
        logger.info(f"[{agent_name}] Skipping: {reason}")
        return True

    result = _run_agent(agent_name, repo_config, agent_config, agent_state)

    return postflight.run(repo_config, agent_name, current_commit, result)


def _run_agent(agent_name, repo_config, agent_config, agent_state) -> AgentRunResult:
    agent_class = AGENT_REGISTRY.get(agent_name)
    if agent_class is None:
        return AgentRunResult(
            status="FAILED_WITH_UNKNOWN_AGENT_ERROR",
            error=str(UnknownAgentError(agent_name))
        )

    try:
        agent = agent_class(repo_config, agent_config, agent_state)
        raw_result = agent.run()
    except GitCommitError as e:
        return AgentRunResult(status="FAILED_WITH_GIT_COMMIT_ERROR", error=str(e))
    except ClaudeMaxTokensError as e:
        return AgentRunResult(status="FAILED_MAX_TOKENS", error=str(e))
    except anthropic.BadRequestError as e:
        return AgentRunResult(status="FAILED_WITH_REQUEST_ERROR", error=str(e))
    except GithubRepoError as e:
        return AgentRunResult(status="FAILED_TO_CREATE_PR_ERROR", error=str(e))
    except GitCheckoutBranchError as e:
        return AgentRunResult(status="FAILED_GIT_BRANCH_ERROR", error=str(e))
    except Exception as e:
        return AgentRunResult(status="FAILED_WITH_ERROR", error=repr(e))

    if raw_result and raw_result.get("pr_url") and raw_result.get("pr_number"):
        return AgentRunResult(
            status="SUCCESS",
            pr_url=raw_result["pr_url"],
            pr_number=raw_result["pr_number"],
            branch=raw_result["branch"]
        )

    return AgentRunResult(status="NO_FINDINGS")
