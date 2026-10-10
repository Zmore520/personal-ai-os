"""Heuristic public-source check; reports paths only, never matched secrets."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    r"https?://(?:drive|docs)\.google\.com/[^\s]+",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AIza[A-Za-z0-9_-]{30,}",
    r"sk-[A-Za-z0-9_-]{20,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]
SKIP = {".git", "__pycache__", ".venv", "build", "dist", "workspace", "reports", "ci-demo"}


def main():
    failed = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in {".md", ".py", ".toml", ".json", ".yml", ".yaml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        if any(re.search(pattern, text) for pattern in PATTERNS):
            failed.append(str(path.relative_to(ROOT)))
    if failed:
        print("Potential private material in: " + ", ".join(failed), file=sys.stderr)
        return 1
    print("Public-source heuristic check passed (manual review still required)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
