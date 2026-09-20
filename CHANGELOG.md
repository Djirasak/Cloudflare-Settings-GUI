# Changelog

## [Unreleased] - 2026-09-20

### Added

- Custom frameless, resizable main window with drag-to-move, edge resizing, and
  Windows Aero Snap (drag to the top edge to maximize, left/right edge to split
  the screen)
- Custom title bar with working minimize / maximize-restore / close controls
- Permission Config page — enter email, Account ID, and API Token to verify
  Cloudflare access
- Permission Loading page — silently re-verifies saved credentials behind a
  spinner and skips straight past the login screen
- "Remember me" credential storage via the OS keyring (Windows Credential
  Manager), with `.env` support as a local-dev convenience fallback
- Modal permissions popup listing the scopes granted by a verified token
  (mocked for now — see below)
- `services/cloudflare` — a gateway wrapping the official Cloudflare SDK and a
  facade exposing simple, UI-friendly results with SDK errors translated into
  readable messages
- Full pytest suite colocated with the code it covers (a `tests/` folder next
  to every package), plus GitHub Actions CI running lint and tests on every push
- Project README
- Changelog automation — `scripts/update_changelog.py` renames `[Unreleased]`
  to `[version] - date` on publish, via a GitHub Actions workflow that pulls
  the version and date straight from the GitHub release

### Changed

- Reorganized the UI into `ui/components/` (shared, reusable pieces) and
  `ui/pages/` (one folder per screen), with page-specific components nested
  inside their own page
- Renamed `AuthenticationPage` → `PermissionConfigPage`,
  `LoadingPage` → `PermissionLoadingPage`, `HelloPage` → `MainPage` to reflect
  what each screen actually does

### Fixed

- Ghosting artifact when maximizing the main window, caused by the drop-shadow
  effect re-rendering on abrupt resize — removed the shadow from the resizable
  window and kept it only on fixed-size popups
- A native crash risk from unparented `QTimer.singleShot` callbacks firing
  after their owning widget had already been destroyed

### Known limitations

- `services/cloudflare` is not yet wired into `PermissionConfigPage` — token
  verification and the permissions popup still use mock data
- The main page is a placeholder; zone list and settings management are not
  implemented yet
