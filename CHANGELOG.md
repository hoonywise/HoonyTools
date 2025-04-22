# 📝 Changelog

All notable changes to **HoonyTools** will be documented in this file.

---

## 🔖 v1.1.1 — Credential Isolation Update (2025-04-21)

This release completes a foundational enhancement for multi-schema workflows across all HoonyTools utilities.

### Enhancements

- **Session memory now isolates credentials for DWH and user schema logins**
  - Prevents accidental schema switching when tools are used in mixed order
  - Supports seamless switching between user and DWH tools during the same session
- `session.user_credentials` and `session.dwh_credentials` now independently store logins
- `session.stored_credentials` is used only for displaying the current active user in the footer

### Technical Details

- Refactored `get_db_connection()` in `oracle_db_connector.py` to ensure:
  - `force_shared=True` always uses `session.dwh_credentials`
  - `force_shared=False` always uses `session.user_credentials`
  - Config saving logic is respected per schema and optional per login
- All tools already support schema-scoped connections and require no modification

### Tested Scenarios

- Skipping login at launch, using DWH tool first, then switching to user schema — works correctly
- Save password on either schema — isolated and respected
- UI and credential status display behave as expected

### UI Enhancements

- Added **"Check for Updates"** menu item under Help, linking to the GitHub Releases page
- Cleaned up the **About HoonyTools** popup (removed internal dev notes for a cleaner look)
- Confirmed keyboard shortcut **Alt + H** works to access Help menu (underline behavior is system-controlled)

---

## 🚀 v1.1.0 – Login System Overhaul, Thread Safety, and Versioned Packaging

This milestone release introduces a secure and consistent login flow, thread-safe execution, session-based memory, and a modernized build system with versioned output.

### Login System Enhancements

- New login prompt with **"Save password"** checkbox
- Credentials saved only if explicitly checked
- If unchecked, login prompt will appear every time
- `config.ini` entries are **auto-removed** when checkbox is unchecked
- Unified login logic across **SCFF**, **MIS**, **Excel**, and **Cleanup** tools

### Thread-Safe Oracle Connections

- MIS loader refactored to accept a passed Oracle connection instead of initializing its own
- All login windows are created on the **main thread**, resolving previous crash issues with large files (e.g., FA and SF)
- Eliminated ghost windows and thread violations

### Config & Session Behavior

- Oracle credentials now persist **per user/schema** only when saved
- Session memory used during a single runtime without forcing save
- Prompt respects session status and login method

### Packaging Overhaul

- Output now goes to `build\v1.1.0\HoonyTools\...`
- Distributable ZIP is created at `dist\HoonyTools_v1.1.0.zip`
- All files are placed inside a top-level `HoonyTools/` folder in the archive
- `libs/config.ini` is automatically **excluded** from the ZIP

### Documentation Updates

- Updated `README.md` and `README.txt` to include:
  - Folder structure
  - Login behavior with checkbox
  - Developer note on threading fix for MIS loaders
- Clarified usage of `HoonyTools.pyw` as the new launcher
- Tools list updated to include **SQL View Loader**

### Notable Fixes

- Resolved crash when loading FA/SF files due to Tkinter thread violations
- `get_db_connection()` now always executes in the main thread

---

## 🔁 v1.0.3 – Switch to Python Launcher + ZIP Packaging

This release replaces the standalone `.exe` launcher with a Python-based GUI runner (`.pyw` + `run.bat`), allowing HoonyTools to be distributed cleanly as a ZIP without triggering antivirus or requiring expensive code signing.

### Key Changes

- Switched from EXE to `.pyw` launcher (`HoonyTools.pyw`)
- GUI now runs silently via `pythonw`
- Included `run.bat` for terminal-free launching on Windows
- EXE and PyInstaller packaging removed

### Packaging Method Updated

- New structure: `dist/HoonyTools_v1.0.3.zip`
- ZIP contains clean folder layout under `HoonyTools/`
- `RELEASE/` folder excluded from Git
- Build script (`build_pkg.bat`) introduced for repeatable packaging

### Documentation Update

- `README.md` rewritten to match ZIP-based installation and usage
- Setup guidance for Python 3.13+
- Included folder structure and launcher behavior
- New `README.txt` added for Windows users

### Notes

- All original GUI functionality remains intact
- EXE-free model avoids SmartScreen warnings
- Ideal for Python-capable teams, schools, or secure organizations

---

## [v1.0.2] – Auto Indexing + Terminology Cleanup

### New Features

- Added automatic index creation for common keys:
  - SCFF Loader: indexes `STUDENT_ID` and `ACYR`
  - MIS Loader: indexes `GI90_RECORD_CODE`, `GI01_DISTRICT_COLLEGE_ID`, `GI03_TERM_ID`
  - Excel/CSV Loader: indexes `PIDM`, `TERM`, `STUDENT_ID` (if columns exist)

### Enhancements

- Shortened key field types to prevent `ORA-01450` (max key length exceeded)
- Index creation now runs even if table already exists (with safe error handling)
- Added user notice in Excel sheet loader GUI: indexable columns will be indexed
- Optional CSV rename prompt added to match Excel sheet behavior

### Terminology Cleanup

- Replaced all references to “Aid Year” with “academic year (ACYR)”
- Updated README and SCFF loader logic to explain 2324 → 2023 `ACYR` conversion for Banner compatibility

### Docs

- Added 📈 Automatic Indexing section to README
- Clarified SCFF loader behavior and folder logic

---

## [v1.0.1] – ACYR Terminology Fix and Licensing Clarification

This release fixes a mislabeling issue across SCFF-related scripts and documentation, where `AIDY` (Aid Year) was mistakenly used instead of the correct term `ACYR` (Academic Year). All relevant code, UI labels, and documentation have been updated to reflect this correction.

In addition, licensing language has been refined across the splash screen, README, and LICENSE files to replace "institutional use" with the more neutral term "enterprise use." This ensures clarity while encouraging responsible adoption within larger teams or departments.

🔧 Changes Included:

- Renamed all references of `AIDY` to `ACYR` across:
  - `scff_data_loader.py`
  - `launcher_gui.py`
  - `table_cleanup_gui.py`
  - `README.md`
- Updated UI labels and logs for consistent terminology
- Reworded licensing language to refer to "enterprise use" instead of "institutional use"
- Splash screen text updated to reflect softer messaging

✅ This update aligns the SCFF tools with naming standards and improves the user experience and adoption clarity for workplace environments.

---

## [v1.0.0] – Initial Public Release: Your Oracle-powered data Swiss Army knife

HoonyTools v1.0.0 is now live!

This marks the first public release of HoonyTools — a portable, no-install Python utility suite designed for analysts and data teams working with Oracle.

🔧 Highlights

- **SQL View Loader**  
  Create or replace Oracle views directly from pasted SQL, with support for your own schema or shared DWH.

- **SCFF Loader**  
  Automatically ingests SCFF text files by ACYR. Supports rollback on abort and skips blank/duplicate lines.

- **MIS Loader**  
  Parses fixed-width `.dat` files using dynamic layouts and loads them into safe `_IN` tables. Auto-detects TERM.

- **Excel/CSV Loader**  
  Uploads Excel sheets or CSVs as new tables with custom names. Supports multiple tabs and blank row cleanup.

- **Table Cleanup Tools**  
  Delete SCFF and MIS records by ACYR or TERM. Also includes general-purpose safe table cleanup by schema.

- **Session Login Support**  
  Shared login popup at launch with support for session or DWH schema use across all tools.

- **Abort-Safe Execution**  
  Tools track new tables and rollback inserts on abort, keeping your Oracle schema clean.

🧭 GUI Tool Legend

| Icon | Meaning                      |
|------|------------------------------|
| ✅   | Uses your Oracle session login |
| 🔒   | Uses shared DWH schema login  |
| 🆕   | New in this version           |
