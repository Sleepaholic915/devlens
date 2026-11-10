
from pathlib import Path


class CodeTools:
    """Read-only tools for investigating a Python repository."""

    MAX_FILE_BYTES = 100_000
    MAX_READ_LINES = 80
    MAX_SEARCH_RESULTS = 20

    SKIP_DIRS = {
        ".git", ".venv", "venv", "__pycache__",
        ".pytest_cache", "node_modules", ".mypy_cache",
    }

    def __init__(self, repo_root: str | Path):
        self.root = Path(repo_root).resolve(strict=True)

        if not self.root.is_dir():
            raise ValueError("Repository root must be a directory")

    def _safe_path(self, relative_path: str) -> Path:
        """Resolve a path and prevent escaping the repository root."""
        path = Path(relative_path)

        if path.is_absolute():
            raise ValueError("Absolute paths are not allowed")

        resolved = (self.root / path).resolve()

        if not resolved.is_relative_to(self.root):
            raise ValueError("Path escapes repository root")

        return resolved

    def _python_files(self):
        """Yield eligible Python files in deterministic order."""
        for path in sorted(self.root.rglob("*.py")):
            relative = path.relative_to(self.root)

            if any(part in self.SKIP_DIRS for part in relative.parts):
                continue

            # Reject symlinks, including symlinked parent directories.
            if any(
                part.is_symlink()
                for part in [path, *path.parents]
                if part != self.root
            ):
                continue

            if not path.is_file():
                continue

            if path.stat().st_size > self.MAX_FILE_BYTES:
                continue

            yield path

    def search_code(self, query: str) -> list[dict]:
        """Search Python source files for a literal substring."""
        if not query or len(query) > 200:
            raise ValueError("Query must be 1-200 characters")

        results = []
        needle = query.casefold()

        for path in self._python_files():
            try:
                with path.open("r", encoding="utf-8") as file:
                    for line_number, line in enumerate(file, start=1):
                        if needle in line.casefold():
                            results.append({
                                "file": path.relative_to(self.root).as_posix(),
                                "line": line_number,
                                "content": line.strip()[:300],
                            })

                            if len(results) >= self.MAX_SEARCH_RESULTS:
                                return results
            except (UnicodeError, OSError):
                continue

        return results

    def read_file(
        self,
        relative_path: str,
        start_line: int = 1,
        end_line: int = 80,
    ) -> dict:
        """Read a bounded range of lines from a Python source file."""
        if start_line < 1 or end_line < start_line:
            raise ValueError("Invalid line range")

        if end_line - start_line + 1 > self.MAX_READ_LINES:
            raise ValueError("Requested too many lines")

        path = self._safe_path(relative_path)

        if path.suffix != ".py":
            raise ValueError("Only Python files are supported")

        if any(
            part in self.SKIP_DIRS
            for part in path.relative_to(self.root).parts
        ):
            raise ValueError("Access to this directory is blocked")

        if not path.is_file():
            raise FileNotFoundError(relative_path)

        if path.stat().st_size > self.MAX_FILE_BYTES:
            raise ValueError("File exceeds size limit")

        lines = []

        with path.open("r", encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                if number > end_line:
                    break
                if number >= start_line:
                    lines.append(f"{number}: {line.rstrip()}")

        return {
            "file": path.relative_to(self.root).as_posix(),
            "start_line": start_line,
            "end_line": start_line + len(lines) - 1,
            "content": "\n".join(lines),
        }
