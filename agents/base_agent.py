from pathlib import Path
from lib.claude_client import call_claude
from lib.git_runner import REPO_DIR
import fnmatch

MAX_SOURCE_FILE_SIZE_KB = 100
MAX_TOTAL_TOKENS = 80000
CHARS_PER_TOKEN = 4
MAX_UNICODE_ERRORS = 3

class BaseAgent:

    def __init__(self, repo_config, agent_config, agent_state):
        self.repo_config = repo_config
        self.agent_config = agent_config
        self.agent_state = agent_state
        self.repo_path = Path(REPO_DIR) / repo_config["name"]

    def load_source_files(self):
        pattern = self.agent_config["file_pattern"]
        ignore_patterns = self.agent_config.get("ignore_paths", [])
        files = {}
        total_chars = 0
        unicode_errors = 0

        for path in sorted(self.repo_path.glob(pattern)):
            relative = str(path.relative_to(self.repo_path))

            if any(fnmatch.fnmatch(relative, ignore) for ignore in ignore_patterns):
                continue

            size_kb = path.stat().st_size / 1024
            if size_kb > MAX_SOURCE_FILE_SIZE_KB:
                print(f"Skipping '{relative}': file too large ({size_kb:.1f} KB, limit {MAX_SOURCE_FILE_SIZE_KB} KB)")
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                unicode_errors += 1
                print(f"Skipping '{relative}': could not decode as UTF-8 ({unicode_errors}/{MAX_UNICODE_ERRORS} unicode errors)")
                if unicode_errors >= MAX_UNICODE_ERRORS:
                    raise RuntimeError(
                        f"Aborting: {unicode_errors} files could not be decoded as UTF-8. "
                        f"Check that '{pattern}' is not matching binary files."
                    )
                continue

            if (total_chars + len(content)) / CHARS_PER_TOKEN > MAX_TOTAL_TOKENS:
                print(f"Skipping '{relative}': token budget exhausted (limit {MAX_TOTAL_TOKENS} tokens)")
                continue

            files[relative] = content
            total_chars += len(content)

        return files
    
    def load_context_files(self):
        """
        Reads fixed context files (KNOWN_ISSUES, REVIEW_AGENT_NOTES) and any
        glob-matched documentation files defined in agent_config.
        Returns dict of {label: content} — missing files are skipped, not errors.
        """
        context = {}

        # Fixed files — paths come from agent_config
        for key in ("issues_file_path", "notes_file_path"):
            rel_path = self.agent_config.get(key)
            if rel_path:
                full_path = self.repo_path / rel_path
                if full_path.exists():
                    context[key] = full_path.read_text(encoding="utf-8")

        # Glob-matched documentation files
        docs = {}
        for pattern in self.agent_config.get("context_file_paths", []):
            for path in self.repo_path.glob(pattern):
                relative = str(path.relative_to(self.repo_path))
                docs[relative] = path.read_text(encoding="utf-8")
        context["docs"] = docs

        return context

    def call_claude(self, system_prompt, user_message, tools=None, tool_choice=None):
        """Calls Claude API. Returns tool input dict if tools provided, otherwise raw response text."""
        return call_claude(system_prompt, user_message, tools=tools, tool_choice=tool_choice)

    def run(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")
