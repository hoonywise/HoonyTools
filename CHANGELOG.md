# 📝 Changelog

All notable changes to **HoonyTools** will be documented in this file.

---

## [v1.0.7] – Public Ready, DSN Flexible, and GUI Polish

**Released:** 2025-04-14

Highlights:

- Public DSN Support: Tools now allow user-defined DSNs, making HoonyTools compatible with any Oracle environment.
- DWH Login Popup: SCFF and MIS loaders now use the login popup instead of hardcoded credentials.
- Credential Persistence: DWH credentials are securely stored in `libs/config.ini` after first use.
- Splash Screen Polish: School logo removed, Hoonywise branding refined, fade-in for "Created by" label.
- Excel/CSV Loader: Now prompts for login **before** file selection.
- Safe Exit & Taskbar Ownership: `safe_exit()` pattern formalized and documented.
- New README and LICENSE: Fully updated for public GitHub release under a custom open-source license.

✅ This is the first public release, marking HoonyTools as officially open source.

---

## [v1.0.6] – Live Status Indicator, UI Polish, and SQL Loader Integration

**Released:** 2025-04-13

✨ Highlights:

- 🟢/⏳ Dynamic status indicator added to show tool activity in real-time (bottom-right corner)
- 🧵 Excel/CSV Loader now runs in a separate thread (Abort button is responsive during load)
- 🧠 SQL View Loader now detects window close and resets status light properly
- 🖱️ Upgraded dropdown to `ttk.Combobox` for modern, consistent selection UI
- 🧭 Refined GUI layout:
  - "Select Tool:" label aligned inline with dropdown
  - "Logged in as" footer moved to bottom-left
  - Vertical spacing and padding optimized
- 🧼 Final polish: all tools now reset status indicator even on errors or user abort

✅ Ready for portable EXE build and full deployment.

---

## [v1.0.5] – Final UX Polish: Autofocus, Enter-to-Submit, Sheet Highlighting

**Released:** 2025-04-13

✨ User Input Enhancements:

- All input dialogs now auto-focus the most relevant field:

  - Username (login), Password (if prefilled), AIDY/TERM (SCFF/MIS), First sheet field (Excel rename)
- Keyboard-friendly: **Enter** now submits all input dialogs (no mouse needed)

📊 Excel Sheet Rename Improvements:

- First field auto-highlighted for instant overwrite

🪟 Taskbar Icon Fix:

- Hidden anchoring window now fully aligned behind login for seamless UX


---

## [v1.0.4] – Dual Icon Fix Stability

**Released:** 2025-04-13

- 🛠 Fixed taskbar icon showing as feather in login or launcher windows
- 🪄 Login window now built using `Toplevel` over hidden root for better icon ownership
- 🔒 Preserved clean shutdown using `safe_exit()`
- ✅ All tools tested and verified post-fix

---

## [v1.0.3] – Final Icon Stability Release

**Released:** 2025-04-13

- 🛠️ Refined `safe_exit()` to cleanly destroy the GUI and background taskbar anchor
- 🖼️ Ensured taskbar icon consistently uses Hoonywise logo across all windows
- 🧪 Full test of extractors, loaders, and config workflows

---

## [v1.0.2] – Finalized HoonyTools EXE with Icon Fix & Secure Config Flow

**Released:** 2025-04-12

- 🚀 Packaged as standalone EXE with embedded icon
- 🔐 `config.ini` created securely per user (not bundled in EXE)
- 📁 Auto-creates `SCFF/` and `MIS/` folders on first run
- ✅ Oracle login now prompts once using unified form
- 🖼️ Fixed persistent feather icon — now always Hoonywise logo

---

