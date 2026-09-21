# Changelog

## [Unreleased] - 2026-09-20

### Added

- Bundled Sarabun (Google Fonts, OFL-licensed) as the app font — Segoe UI's
  Thai glyphs looked rough by comparison. Regular/SemiBold/Bold weights are
  loaded from `assets/fonts/` at startup via `QFontDatabase`. Its tone/vowel
  marks were getting clipped at the top of `QLineEdit`s, `QPushButton`s, and
  even auto-sized `QLabel`s — its shipped `hhea`/`OS2` ascent (1068 units)
  left too little headroom above its own combining marks (up to ~971 units,
  before accounting for mark-attachment offsets), and the same clipping
  happened with Google's CDN-served files too, so it wasn't a bad download.
  CSS padding tweaks per widget type were unreliable (fixed one spot,
  centering broke, still clipped elsewhere), so the font files themselves
  were patched with `fonttools` to raise that ascent to 1300 units — the
  real fix, and it needed no stylesheet padding hacks at all
- Custom frameless, resizable main window with drag-to-move, edge resizing, and
  Windows Aero Snap (drag to the top edge to maximize, left/right edge to split
  the screen)
- Custom title bar with working minimize / maximize-restore / close controls
- Permission Config page — enter email, Account ID, and API Token to verify
  Cloudflare access
- Permission Loading page — silently re-verifies saved credentials behind a
  spinner and skips straight past the login screen. Verification runs as
  three visible, sequential steps, each ticking green (✓) or red (✗) as it
  resolves — later steps stay in a neutral pending state until reached:
  1. **ตรวจสอบ API Token** — `user.tokens.verify()` for an active status
  2. **ตรวจสอบ Account** — `accounts.get()` confirms the entered Account ID
  3. **ตรวจสอบสิทธิ์ (Permission)** — `user.tokens.list()` finds this app's
     own personal API Token by name (must start with `xgui_` or `gui_`,
     case-insensitive — a user can hold several tokens), then lists every
     permission from the fixed set in `services/cloudflare/permissions.py`
     as its own green/red row, checked against the token's actual
     `permission_groups`
  The found token's id is cached via `keyring` for later reuse.
  `CloudflareFacade.check_credentials()` was split into `check_token()`,
  `check_account()`, and `check_permissions()` so the page can dispatch and
  render each step independently. A failure at any step clears the saved
  credentials and bounces back to the Permission Config page with the reason
  shown, after a brief pause so the checklist's final state is visible first
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
- Main page now shows a real 70/30 two-panel layout: the right sidebar lists
  the Cloudflare domains on the verified account as cards (live API data, no
  more mock), the left panel is reserved empty for future use
- Each domain card now has a "Development Mode" toggle and a "ล้างแคช" (purge
  cache) button, backed by the `CloudflareFacade` methods above
- Toast component (`ui/components/toast.py`) — a dismissible bar docked at
  the bottom of the main page that shows success/error feedback for domain
  card actions (dev mode toggle, purge cache) and auto-hides after 3s.
  `RightPanelPartial` raises an `action_feedback` signal for these instead
  of writing them into its own top-of-panel status label
- `ToggleSwitch` component (`ui/components/toggle_switch.py`) — a custom
  pill-shaped on/off switch used for the domain card's Development Mode
  control, on its own row above "ล้างแคช"
- Domain card's status is a colored pill badge shown above the domain name,
  and the card's border matches the same color as the badge (green for
  `active`, gray otherwise)
- Main page's left panel is now a tabbed layout (`LeftPanelPartial`,
  `ui/pages/main/partials/left_panel.py`), styled to match the app's dark
  theme. First tab is "Tunnel", backed by its own `TunnelsPartial`
  (`ui/pages/main/partials/tunnels.py`); "DDNS" is still an inline
  placeholder pending the same treatment, currently showing "เร็ว ๆ นี้"
- Tunnel tab lists the account's real Cloudflare Tunnels (name and status)
  via `zero_trust.tunnels.list()` — `CloudflareGateway.list_tunnels()` and
  `CloudflareFacade.list_tunnels()` follow the same gateway/facade/
  `TunnelInfo`/`TunnelListResult` shape as the existing domain list.
  `MainPage.load_domains()` was renamed to `load_account_data()` since it
  now kicks off both the domain list and the tunnel list on successful login

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
  verification — the found permissions are no longer shown in a popup along
  the way
- Main page's domain sidebar split out of `main_page.py` into
  `ui/pages/main/partials/right_panel.py` (the page section — owns its own
  data, loading state, and API calls; later renamed from `domain_sidebar.py`
  to `right_panel.py`/`RightPanelPartial` to mirror the left panel) and
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
- `AuthFlowDialog.set_content()` (swapping between the config/loading/error
  screens) logged `UpdateLayeredWindowIndirect failed` and ghosted on Windows
  — the translucent frameless dialog's incremental resize produced an invalid
  dirty rect. Fixed by hiding and reshowing the dialog around the swap so
  Windows builds a fresh layered surface instead
- `RightPanelPartial` and `TunnelsPartial` each owned a `QThreadPool(self)` —
  if the widget were destroyed while a worker was still in flight (e.g. app
  quit during a slow request), the pool's destructor blocks on
  `waitForDone()` while holding the GIL the worker thread needs to finish,
  deadlocking. Switched both to the shared `QThreadPool.globalInstance()`,
  which outlives any single widget
- `TestTitleBarEdgeSnapping::test_dragging_to_left_edge_snaps_to_left_half`
  failed deterministically on a multi-monitor dev machine. Its `_drag` test
  helper mapped the release position's screen coordinate to a local point
  once, before the simulated drag — but `TitleBar.mouseMoveEvent` actually
  moves the window (mirroring a real drag), so that stale local point
  overshot onto the second monitor once re-globalized against the window's
  new position at release time, landing outside both screens' snap
  thresholds. Fixed by recomputing the local point immediately before each
  of the move and release events

### Known limitations

- `PermissionsDialog` (the "สิทธิ์การเข้าถึงที่ตรวจพบ" popup listing detected
  permissions) is built and tested but not wired into the app anywhere —
  nothing yet turns a verified token's permission groups into the list it
  expects
