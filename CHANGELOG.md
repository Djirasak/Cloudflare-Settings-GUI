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
- "ปิดโปรแกรม" (close) button on the Permission Config page — previously the
  only way out of that screen was killing the process, since it's a modal
  popup with no title bar
- Main page now shows a real 80/20 two-panel layout: the right sidebar lists
  the Cloudflare domains on the verified account as cards (live API data, no
  more mock), the left panel is reserved empty for future use
- Each domain card now has a "Development Mode" toggle and a "ล้างแคช" (purge
  cache) button, backed by the `CloudflareFacade` methods above
- Toast component (`ui/components/toast.py`) — a dismissible bar docked at
  the bottom of the main page that shows success/error feedback for domain
  card actions (dev mode toggle, purge cache) and auto-hides after 3s.
  `DomainSidebarPartial` raises an `action_feedback` signal for these instead
  of writing them into its own top-of-panel status label
- `ToggleSwitch` component (`ui/components/toggle_switch.py`) — a custom
  pill-shaped on/off switch used for the domain card's Development Mode
  control, on its own row above "ล้างแคช"
- Domain card's status is a colored pill badge shown above the domain name,
  and the card's border matches the same color as the badge (green for
  `active`, gray otherwise)

### Changed

- Reorganized the UI into `ui/components/` (shared, reusable pieces) and
  `ui/pages/` (one folder per screen), with page-specific components nested
  inside their own page
- Renamed `AuthenticationPage` → `PermissionConfigPage`,
  `LoadingPage` → `PermissionLoadingPage`, `HelloPage` → `MainPage` to reflect
  what each screen actually does
- Renamed the `cfgui` console script to `dev`, and added `cleanup` alongside
  it for the credential-clearing script above
- `PermissionConfigPage.continue_requested` now carries the entered Account ID
  and API Token so the main page can load real domain data right after
  verification, instead of a bare signal
- Permission Config page no longer has a separate "ตรวจสอบสิทธิ์" (verify)
  step — entering credentials and clicking "ดำเนินการต่อ" (continue) goes
  straight to the Permission Loading page, which now performs the
  verification (still mocked, per the known limitation below) — the found
  permissions are no longer shown in a popup along the way
- Main page's domain sidebar split out of `main_page.py` into
  `ui/pages/main/partials/domain_sidebar.py` (the page section — owns its own
  data, loading state, and API calls) and
  `ui/pages/main/components/domain_card.py` (a dumb widget that only emits
  intent signals), so `main_page.py` stays a thin layout shell as more
  sections get added later
- Domain loading and every card action (dev mode toggle, purge cache) now run
  on a `QThreadPool` worker (`ui/components/worker.py`) instead of blocking
  the GUI thread — results come back via Qt's queued signals, so a slow
  request no longer freezes the window

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

- `services/cloudflare`'s credential *verification* is not yet wired into
  `PermissionLoadingPage` — the verify step and permissions popup still use
  mock data (domain listing on the main page does use the real API)
