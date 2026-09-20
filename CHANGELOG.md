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
- `cleanup` console script (and a double-click `cleanup.bat` for
  convenience) to wipe saved keyring credentials — needed whenever `.env` is
  updated, since a saved keyring value otherwise takes priority over it
- `CloudflareFacade.list_zones()` — fetches the real domain list and maps SDK
  `Zone` objects into simple `DomainInfo` values for the UI
- `CloudflareGateway` logs every HTTP request and response (method, URL, and
  body) it sends via httpx event hooks — wired up once at construction so
  every current and future SDK call gets logged for free, instead of a
  `print()` in each gateway method. Bodies are pretty-printed as indented
  JSON and status lines are color-coded (green/yellow/red by status code)
- `CloudflareGateway`/`CloudflareFacade` gained `set_development_mode()` and
  `purge_cache()` for per-domain dev-mode toggling and cache purging, and
  `DomainInfo` now carries the zone ID needed to call them
- `DomainInfo.dev_mode_enabled` is derived from the `development_mode` field
  the SDK's `Zone` object already returns (seconds until it expires, positive
  = on, `<=0` = off), so the current dev-mode state is available with no
  extra API call per domain

### Changed

- Reorganized the UI into `ui/components/` (shared, reusable pieces) and
  `ui/pages/` (one folder per screen), with page-specific components nested
  inside their own page
- Renamed `AuthenticationPage` → `PermissionConfigPage`,
  `LoadingPage` → `PermissionLoadingPage`, `HelloPage` → `MainPage` to reflect
  what each screen actually does
- Renamed the `cfgui` console script to `dev`, and added `cleanup` alongside
  it for the credential-clearing script above

### Fixed

- Ghosting artifact when maximizing the main window, caused by the drop-shadow
  effect re-rendering on abrupt resize — removed the shadow from the resizable
  window and kept it only on fixed-size popups
- A native crash risk from unparented `QTimer.singleShot` callbacks firing
  after their owning widget had already been destroyed
- Every real Cloudflare API call was failing with `403 Missing X-Auth-Key
  header`, even with a valid, active API token. Cause: the Cloudflare SDK
  falls back to `CLOUDFLARE_EMAIL` / `CLOUDFLARE_API_KEY` from the environment
  whenever they aren't explicitly passed, and once `api_email` resolves to
  any value it silently prioritizes legacy Email+Key auth over the Bearer
  token — and this app's own `.env` sets `CLOUDFLARE_EMAIL` for UI prefill.
  Fixed by explicitly clearing `api_email` / `api_key` on the constructed SDK
  client in `CloudflareGateway`
- `cleanup` crashed with `UnicodeEncodeError` on Windows terminals using a
  legacy codepage (cmd.exe, some Git Bash setups) because its confirmation
  message is in Thai — fixed by reconfiguring stdout to UTF-8 first

### Known limitations

- `services/cloudflare` is not yet wired into `PermissionConfigPage` — token
  verification and the permissions popup still use mock data
- The main page is a placeholder; zone list and settings management are not
  implemented yet
