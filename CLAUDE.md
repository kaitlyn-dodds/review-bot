# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

An automated pipeline that runs on a home server (Docker on Proxmox LXC) and analyzes personal code repositories for logic bugs and deviations from project goals. Claude performs the analysis and proposes findings via a GitHub PR updating `KNOWN_ISSUES.md`. The developer reviews and merges or closes — false positives are noted in `REVIEW_AGENT_NOTES.md` to suppress re-flagging.

## Architecture

The project is an **agent-based pipeline** triggered by cron:

- **`runner.py`** — entry point. Receives the agent name as an argument, loads all configs in `configs/` that have that agent enabled, and dispatches the agent for each qualifying repo.
- **`configs/{repo-name}.yaml`** — per-repo config: repo path, GitHub details (owner, repo name, branch), which agents are enabled, and file glob patterns to scan (e.g. `**/*.gd`).
- **`state/{repo-name}.json`** — auto-created on first run. Tracks last evaluated commit hash and open PR status. This directory is gitignored.
- **`agents/base_agent.py`** — base class handling common logic: reading context files (`KNOWN_ISSUES.md`, `REVIEW_AGENT_NOTES.md`, `README.md`, `ARCHITECTURE.md`, `OVERVIEW.md`), calling Claude, returning structured results.
- **`agents/issue_scanner.py`** — concrete agent. Checks for open bot PRs and commit hash changes before running. Feeds the codebase + context to Claude. Creates a branch named `bot/issue-scan-{commit-hash}`, commits an updated `KNOWN_ISSUES.md`, and opens a PR.
- **`prompts/issue_scanner.md`** — the Claude system prompt for the issue scanner. Not hardcoded in the script.
- **`lib/github.py`**, **`lib/git.py`**, **`lib/claude.py`** — shared library modules for GitHub API, git operations, and Claude API calls respectively.

## Key Behaviors

- **Skip logic**: If HEAD matches the last evaluated commit hash AND no open bot PR needs attention, the run is skipped.
- **No duplicate PRs**: A new PR is never opened while one from a previous scan is still open.
- **False positive suppression**: `REVIEW_AGENT_NOTES.md` in the target repo tells the bot what not to re-flag.
- **Secrets**: GitHub token and SSH deploy key are passed as environment variables — nothing secret is baked in.

## Planned Scaffold (not yet fully implemented)

```
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
    {repo-name}.yaml
  state/
    {repo-name}.json   # gitignored
```

## MVP Scope

In scope: issue scanner agent only. Out of scope: auto-fixing, diff-scoped scans, notifications beyond GitHub PRs, any other agents.

## Working Guidelines

- **Ask before assuming**: If a requirement is ambiguous or an implementation decision has multiple valid options, ask for clarification before proceeding. Do not silently pick one path.
- **Implement only what is asked**: Do not implement adjacent functions, refactor surrounding code, or add features beyond the explicit request.
- **Scope confirmations**: If asked to implement one function, implement only that function — not the full phase or related helpers.
