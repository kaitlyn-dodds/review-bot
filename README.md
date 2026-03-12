
# Review Bot

## What it is

An automated pipeline that runs on my home server and analyzes my personal code repositories for logic bugs, inconsistencies, and deviations from the project's stated goals. Calude is utalized to perform the analysis and proposes findings via a GitHub pull request for human review before anything is committed to the project.

## How it works

A cron job on the host triggers the review process on a configurable schedule. The review process starts by pulling the latest code from the target repository, feeds it to Claude along with context files, and if new issues are found, pushes a branch and opens a PR with an updated `KNOWN_ISSUES.md`. The developer reviews the PR and either merges it or closes it — in the case of false positives, they add a note to `REVIEW_AGENT_NOTES.md` so the bot won't re-flag the same thing in future scans.

## MVP Requirements

**Infrastructure**
- Runs wihtin a Docker container deployed on a Proxmox LXC (Ubuntu server image)
- Container is stateless — all persistent data lives in host-mounted volumes
- Cron job triggers the review process per project. Project history and configuation is stored per repo and updated each time the process runs. 
- Should be built to be extensible with possible future enhancements such as "bug fixer", "test writer", etc. components that can easily be configured to run against the repositories. 

**Bot framework**
- `runner.py` acts as the entry point — loads config, checks state, dispatches agents
- Per-repo config files in `configs/` define repo path, GitHub details, and which agents are enabled
- Per-repo state files in `state/` track last evaluated commit hash and open PR status
- At the start of each run the runner checks the status of any open PRs before deciding whether to scan
- If the current HEAD matches the last evaluated commit and no PRs need attention, skip the run
- Shared library modules for git operations, GitHub API calls, and Claude API calls
- Agent base class that handles common logic — reading context files, calling Claude, returning structured results

**Issue scanner agent**
- Reads the full codebase (scoped by file pattern defined in config, e.g. `**/*.gd`)
- Reads `KNOWN_ISSUES.md` and `REVIEW_AGENT_NOTES.md` as context
- Reads any further documentation such as the repo `README.md`, `ARCHITECTURE.md`, and `OVERVIEW.md` files that would provide context on the repo. 
- Calls Claude API with a system prompt that describes the project's goals and what to look for
- Returns only issues that are not already present in `KNOWN_ISSUES.md` or excluded by `REVIEW_AGENT_NOTES.md`
- System prompt lives in `prompts/issue_scanner.md`, not hardcoded in the script

**GitHub integration**
- Creates a new branch named with the agent name and commit hash (e.g. `bot/issue-scan-a3f9c12`)
- Commits proposed changes to `KNOWN_ISSUES.md` on that branch
- Opens a PR against main with a summary of findings
- Does not open a new PR if one from a previous scan is still open

**Secrets and config**
- GitHub API token and SSH deploy key passed in as environment variables
- Nothing repo-specific or secret is baked into the Docker image
- `state/` is gitignored

## Explicitly out of scope for MVP

- Automatically fixing issues
- Scoping scans to only diff'd files (tracked as a future improvement once full scans are stable)
- Any agent other than the issue scanner
- Any notification mechanism other than the GitHub PR

## Future directions

- Additional agents: documentation checker, fix suggester, consistency checker
- Diff-scoped scanning as the codebase grows
- Support for multiple repos via additional config files
- PR comment parsing for richer feedback loops

# Suggested Project Scaffold

review-bot/
  runner.py
  agents/
    base_agent.py
    issue_scanner.py
  prompts/
    issue_scanner.md
  lib/
    github.py
    git.py
    claude.py
  configs/
    {repo-name}.yaml     # cannot run against a repo that isn't defined here
  state/
    {repo-name}.json     # auto-created on first run, mirrors config filename
