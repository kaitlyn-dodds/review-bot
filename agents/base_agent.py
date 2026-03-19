import glob
from pathlib import Path
from lib.claude_client import call_claude
import fnmatch

MAX_SOURCE_FILE_SIZE_KB = 100
MAX_TOTAL_TOKENS = 80000
CHARS_PER_TOKEN = 4

class BaseAgent:

    def __init__(self, repo_config, agent_config, agent_state):
        self.repo_config = repo_config
        self.agent_config = agent_config
        self.agent_state = agent_state
        self.repo_path = Path(repo_config["repo_path"])

    def load_source_files(self):
        pattern = self.agent_config["file_pattern"]
        ignore_patterns = self.agent_config.get("ignore_paths", [])
        files = {}
        total_chars = 0
        skipped = []

        for path in sorted(self.repo_path.glob(pattern)):
            # Check against ignore patterns
            relative = path.relative_to(self.repo_path)
            if any(fnmatch.fnmatch(str(relative), ignore) for ignore in ignore_patterns):
                continue

            size_kb = path.stat().st_size / 1024
            if size_kb > MAX_SOURCE_FILE_SIZE_KB:
                skipped.append((str(relative), "too large"))
                continue

            content = path.read_text(encoding="utf-8")
            if (total_chars + len(content)) / CHARS_PER_TOKEN > MAX_TOTAL_TOKENS:
                skipped.append((str(relative), "total limit reached"))
                continue

            files[str(relative)] = content
            total_chars += len(content)

        if skipped:
            print(f"Skipped {len(skipped)} files: {skipped}")

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

    def call_claude(self, system_prompt, user_message):
        """Calls Claude API, returns raw response text."""
        return call_claude(system_prompt, user_message)

    def run(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")
