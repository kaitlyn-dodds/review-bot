import json
from pathlib import Path

from agents.base_agent import BaseAgent
from lib.git_runner import create_branch, commit_file
from lib.github_client import open_pr


PROMPTS_DIR = Path("prompts")


class IssueScannerAgent(BaseAgent):

    def run(self):
        # 1. Load prompt
        system_prompt = (PROMPTS_DIR / "issue_scanner.md").read_text(encoding="utf-8")
        
        # 2. Load repo files
        sources = self.load_source_files()
        context = self.load_context_files()

        # 3. Build user message
        user_message = self._build_user_message(sources, context)

        # # 4. Call Claude
        raw_response = self.call_claude(system_prompt, user_message)

        # # 5. Parse findings
        findings = self._parse_findings(raw_response)
        if not findings:
            print("No new findings.")
            return None

        # # 6. Write updated KNOWN_ISSUES.md
        print("Adding findings: ", findings)
        updated_content = self._build_known_issues(findings, context)
        issues_path = self.repo_path / self.agent_config["issues_file_path"]
        issues_path.write_text(updated_content, encoding="utf-8")

        # # 7. Create branch, commit, open PR
        commit_hash = self.agent_state["last_run"]["commit"]  # set by runner before dispatch
        branch_name = f"bot/issue-scan-{commit_hash[:7]}"

        create_branch(self.repo_config["name"], branch_name)
        commit_file(self.repo_config["name"], str(issues_path), "bot: update KNOWN_ISSUES.md")
        # pr_url, pr_number = open_pr(
        #     self.repo_config,
        #     branch_name,
        #     title=f"[Bot] Issue scan — {commit_hash[:7]}",
        #     body=self._build_pr_body(findings),
        # )

        # return {"pr_url": pr_url, "pr_number": pr_number, "findings": findings}

    def _build_user_message(self, sources, context):
        parts = []

        if "issues_file_path" in context:
            parts.append("## Already Known Issues (do not re-flag)\n\n" + context["issues_file_path"])

        if "notes_file_path" in context:
            parts.append("## Review Agent Notes (suppressed findings)\n\n" + context["notes_file_path"])

        for filename, content in context.get("docs", {}).items():
            parts.append(f"## {filename}\n\n{content}")

        parts.append("## Source Files\n")
        for path, content in sources.items():
            parts.append(f"### {path}\n```\n{content}\n```")

        return "\n\n".join(parts)

    def _parse_findings(self, raw_response):
        """Extracts JSON findings block from Claude's response."""
        try:
            start = raw_response.index("```json") + 7
            end = raw_response.index("```", start)
            return json.loads(raw_response[start:end].strip())
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to parse findings: {e}")
            return []

    def _build_known_issues(self, findings, context):
        """Appends new findings to existing KNOWN_ISSUES.md content."""
        existing = context.get("issues_file_path", "# Known Issues\n")
        new_entries = []
        for f in findings:
            new_entries.append(
                f"## {f['title']}\n"
                f"**Severity:** {f['severity']}  \n"
                f"**File:** `{f['file']}`  \n\n"
                f"{f['description']}\n\n"
                f"**Suggested fix:** {f['suggested_fix']}\n"
            )
        return existing.rstrip() + "\n\n" + "\n\n---\n\n".join(new_entries)

    def _build_pr_body(self, findings):
        lines = [f"## Issue Scan Findings\n\n{len(findings)} new issue(s) found.\n"]
        for f in findings:
            lines.append(f"- **{f['title']}** (`{f['file']}`) — {f['severity']} severity")
        return "\n".join(lines)
