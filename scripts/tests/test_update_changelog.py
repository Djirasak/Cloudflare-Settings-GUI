from pathlib import Path

import pytest

from scripts.update_changelog import UNRELEASED_HEADER, update_changelog

SAMPLE_CHANGELOG = """# Changelog

## [Unreleased]

## [0.1.0] - 2026-09-20

### Added

- Initial release
"""


class TestUpdateChangelog:
    @pytest.fixture
    def changelog_file(self, tmp_path: Path) -> Path:
        path = tmp_path / "CHANGELOG.md"
        path.write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        return path

    def test_renames_unreleased_and_adds_fresh_section_above_it(self, changelog_file: Path):
        update_changelog(version="1.0.0", release_date="2026-10-15", changelog_path=changelog_file)

        content = changelog_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        assert UNRELEASED_HEADER in lines
        assert "## [1.0.0] - 2026-10-15" in lines
        assert lines.index(UNRELEASED_HEADER) < lines.index("## [1.0.0] - 2026-10-15")

    def test_preserves_existing_release_history(self, changelog_file: Path):
        update_changelog(version="1.0.0", release_date="2026-10-15", changelog_path=changelog_file)

        content = changelog_file.read_text(encoding="utf-8")

        assert "## [0.1.0] - 2026-09-20" in content
        assert "- Initial release" in content

    def test_raises_when_unreleased_heading_is_missing(self, tmp_path: Path):
        path = tmp_path / "CHANGELOG.md"
        path.write_text("# Changelog\n\n## [0.1.0] - 2026-09-20\n", encoding="utf-8")

        with pytest.raises(SystemExit):
            update_changelog(version="1.0.0", release_date="2026-10-15", changelog_path=path)

    def test_strips_hand_maintained_date_suffix_on_unreleased(self, tmp_path: Path):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(
            "# Changelog\n\n## [Unreleased] - 2026-09-25\n\n### Added\n\n- Work in progress\n",
            encoding="utf-8",
        )

        update_changelog(version="1.0.0", release_date="2026-10-15", changelog_path=path)

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        assert UNRELEASED_HEADER in lines
        assert "## [1.0.0] - 2026-10-15" in lines
        assert "- Work in progress" in content
