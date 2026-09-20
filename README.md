# Cloudflare Settings GUI

A native-feeling Windows desktop app for viewing and managing Cloudflare zone settings — built with PyQt6, no browser tab required.

[![CI](https://github.com/Djirasak/Cloudflare-Settings-GUI/actions/workflows/ci.yml/badge.svg)](https://github.com/Djirasak/Cloudflare-Settings-GUI/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.13-blue)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Highlights

- **Custom frameless window** — rounded corners, drop shadow, drag-anywhere title bar with real minimize / maximize-restore / close controls
- **Windows Aero Snap** — drag to the top edge to maximize, to the left/right edge to split the screen, exactly like a native window
- **Remembers you** — credentials are saved to the OS keyring (Windows Credential Manager), never plaintext; uncheck the box and they're wiped
- **Skips the login screen** — if credentials are already remembered, the app verifies silently behind a spinner and drops you straight into the app
- **`.env` support for local dev** — seed `CLOUDFLARE_EMAIL` / `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_API_TOKEN` once and stop retyping them
- **Real Cloudflare API layer** — a typed gateway/facade over the official `cloudflare` SDK, fully unit-tested against mocks (not yet wired into the UI — see [Roadmap](#-roadmap))

## 📸 What it looks like today

A modal permission-check dialog floats over the main window on launch, wired up either to a manual credential form or an auto "verifying with saved credentials" spinner:

```
┌──────────────────────────────────────┐
│ ☁  Cloudflare Settings GUI      – □ ✕ │
├──────────────────────────────────────┤
│                                       │
│   Cloudflare Settings GUI            │
│   กรอกข้อมูลบัญชี Cloudflare...        │
│                                       │
│   อีเมล        [______________]      │
│   Account ID   [______________]      │
│   API Token    [______________]      │
│                                       │
│   ☑ จดจำข้อมูลนี้ไว้ในเครื่องนี้        │
│                                       │
│   [ ตรวจสอบสิทธิ์ ]  [ ดำเนินการต่อ ]  │
└──────────────────────────────────────┘
```

## 🚀 Getting started

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13.

```bash
git clone https://github.com/Djirasak/Cloudflare-Settings-GUI.git
cd Cloudflare-Settings-GUI
uv sync
uv run cfgui
```

### Optional: skip retyping credentials in dev

```bash
cp .env.example .env
# then fill in CLOUDFLARE_EMAIL, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN
```

`.env` is git-ignored — it's for local convenience only. Check "จดจำข้อมูลนี้ไว้ในเครื่องนี้" in the app to persist credentials to the OS keyring instead.

## 🧪 Development

```bash
uv run pytest          # full test suite (offscreen Qt platform, no display needed)
uv run ruff check .    # lint
```

Tests live next to the code they cover — every package has its own `tests/` folder — so adding a test is always a matter of "does this folder have a `tests/` dir yet?"

CI runs both on every push via GitHub Actions (`.github/workflows/ci.yml`).

## 🗂️ Project layout

```
src/cloudflare_settings_gui/
├── credentials.py              # OS keyring read/write/clear
├── services/cloudflare/
│   ├── gateway.py              # thin wrapper over the Cloudflare SDK
│   └── facade.py               # app-facing API, translates SDK errors into results
└── ui/
    ├── components/              # reusable, page-agnostic building blocks
    │   ├── frameless_window.py  # resizable shell: drag, resize, snap, maximize
    │   ├── title_bar.py         # custom title bar + edge-snap logic
    │   ├── shadow_card.py       # rounded, drop-shadowed card used by windows/dialogs
    │   └── auth_flow_dialog.py  # modal popup that hosts the login/loading flow
    └── pages/                   # one folder per screen; page-specific pieces live inside
        ├── permission_config/   # manual credential entry + verification
        ├── permission_loading/  # spinner shown when auto-verifying saved creds
        └── main/                # the screen behind the login modal
```

## 🛣️ Roadmap

- [ ] Wire `services/cloudflare` into `PermissionConfigPage` (currently mocked)
- [ ] Replace the placeholder main page with real zone list + settings management
- [ ] Package as a standalone `.exe` via PyInstaller

## License

MIT — see [LICENSE](LICENSE).
