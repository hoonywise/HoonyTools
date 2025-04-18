# 📝 Changelog

All notable changes to **HoonyTools** will be documented in this file.

---

## [v1.0.2] – Auto Indexing + Terminology Cleanup

✨ New Features:

- Added automatic index creation for common keys:
  - SCFF Loader: indexes `STUDENT_ID` and `ACYR`
  - MIS Loader: indexes `GI90_RECORD_CODE`, `GI01_DISTRICT_COLLEGE_ID`, `GI03_TERM_ID`
  - Excel/CSV Loader: indexes `PIDM`, `TERM`, `STUDENT_ID` (if columns exist)

🔧 Enhancements:

- Shortened key field types to prevent `ORA-01450` (max key length exceeded)
- Index creation now runs even if table already exists (with safe error handling)
- Added user notice in Excel sheet loader GUI: indexable columns will be indexed
- Optional CSV rename prompt added to match Excel sheet behavior

🧼 Terminology Cleanup:

- Replaced all references to “Aid Year” with “academic year (ACYR)”
- Updated README and SCFF loader logic to explain 2324 → 2023 `ACYR` conversion for Banner compatibility

📚 Docs:

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
