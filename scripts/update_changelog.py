"""Renames the '[Unreleased]' CHANGELOG heading to '[<version>] - <date>' and
adds a fresh empty Unreleased section above it. Run by the release-changelog
GitHub Actions workflow when a release is published.

Matches the whole "## [Unreleased]" line, including an optional trailing
"- <date>" that gets hand-maintained during development to track when the
section was last touched — that suffix is dropped since the fresh section
this produces has nothing in it yet.
"""

import re
import sys
from pathlib import Path

CHANGELOG_PATH = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
UNRELEASED_HEADER = "## [Unreleased]"
UNRELEASED_LINE_PATTERN = re.compile(r"^## \[Unreleased\].*$", re.MULTILINE)


def update_changelog(version: str, release_date: str, changelog_path: Path = CHANGELOG_PATH) -> None:
    content = changelog_path.read_text(encoding="utf-8")

    if not UNRELEASED_LINE_PATTERN.search(content):
        raise SystemExit(f"Could not find '{UNRELEASED_HEADER}' in {changelog_path}")

    new_heading = f"{UNRELEASED_HEADER}\n\n## [{version}] - {release_date}"
    content = UNRELEASED_LINE_PATTERN.sub(new_heading, content, count=1)

    changelog_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: update_changelog.py <version> <release_date>")
    update_changelog(version=sys.argv[1], release_date=sys.argv[2])
