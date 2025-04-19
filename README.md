<table>
  <tr>
    <td><img src="https://www.gravatar.com/avatar/cbae675632b5840c0a7dd177e61c8634?s=80" alt="Hoonywise Logo" width="50"></td>
    <td><h1 style="margin-left: 10px;">HoonyTools</h1></td>
  </tr>
</table>

[![](https://img.shields.io/badge/license-Custom-gold)](LICENSE.md)
[![](https://img.shields.io/badge/Donate-PayPal-blue)](https://www.paypal.com/donate/?hosted_button_id=NJSTAENDWQLXS)

---

HoonyTools is an all-in-one Python-based toolkit for loading, transforming, and cleaning data in Oracle databases.  
Originally built for institutional data teams, it has since been expanded into a flexible platform for analysts and researchers in any organization.

Designed with front-end users in mind, HoonyTools features an intuitive GUI that makes it easy to load data into Oracle as tables or views, run batch imports, and perform record-level cleanup.

With built-in support for SCFF, MIS, Excel, and CSV formats, and customizable database connections via user-defined DSNs, HoonyTools is ideal for daily ETL, research, and reporting workflows.

> 💝 **Now open source and available for public use and modification — our gift to the world of analysts who work with data, not database management.**

---

## 🧑‍💻 Quick Start

### Python Required (No EXE)

HoonyTools now runs directly as a Python GUI app — no installation or EXE needed.

**First-Time Setup:**

1. Ensure [Python 3.13+](https://www.python.org/downloads/) is installed
2. Open a terminal in the HoonyTools folder
3. Run:  
   ```
   pip install -r requirements.txt
   ```
4. Launch the app by double-clicking `run.bat` or running:
   ```
   pythonw launcher_gui.pyw
   ```

✅ This launches the GUI with **no terminal window**

---

## 🗂️ Folder Structure

After unzipping `HoonyTools_v1.0.2_python.zip`, you should see:

```
HoonyTools/
├── HoonyTools.pyw         # Main launcher (double-click this)
├── config.py              # Handles path logic
├── setup_config.py        # One-time setup script for DWH login
├── README.txt             # Windows user guide
├── README.md              # This file (GitHub format)
├── LICENSE.md             # Licensing terms
├── CHANGELOG.md           # Release notes
├── requirements.txt       # (Optional) Python modules if running from source)
├── libs/                  # Shared utility modules (Oracle, config, logging, etc.)
│   └── config.ini         # Created at first login if "Save password" is checked
├── loaders/               # SCFF, MIS, and Excel loaders
├── tools/                 # Table cleanup tools and extractors
├── assets/                # Icons and splash images
├── SCFF/
│   ├── Downloads/         # Holds SCFF zip downloads (e.g. scff860.zip)
│   └── SCFF_Data/         # Organized by academic year (ACYR)
│       ├── <ACYR>/        # e.g. 2324/
│       │   ├── Latest/    # Fresh extracts go here
│       │   └── Archive/   # Older extracts are auto-archived here
└── MIS/
    └── .dat input files   # Place your MIS .dat files here
```

Optional: Run `setup_config.py` to securely generate your Oracle DWH login config on first launch.

---

## 🛠️ Setup Requirements

To run HoonyTools, you’ll need the following installed and configured:

---

### ✅ Python 3.13 or Higher

1. Install from the official site:  
   👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. During installation, make sure to check:  
   ✅ “Add Python to PATH”

---

### 🧩 Required Python Packages

Once Python is installed, run the following from the HoonyTools folder:

```
pip install -r requirements.txt
```

This installs all required libraries including:

- `oracledb` (for Oracle connectivity)
- `pandas`, `openpyxl` (for Excel/CSV processing)
- `pywin32`, `pystray`, `Pillow` (for GUI tray features and icon support)

---

### 🛢️ Oracle Instant Client

To connect to Oracle databases, the **Oracle Instant Client** must be installed and properly configured:

1. **Add the Instant Client folder to your system PATH**  
   Example:
   ```
   C:\oracle\instantclient_21_13
   ```

2. **Create a `tnsnames.ora` file** inside your Oracle `network/admin` folder  
   or set the `TNS_ADMIN` environment variable to point to it.

   This file defines named DSNs such as `DWHDB_DB` used by HoonyTools.

   Example entry:
   ```
   DWHDB_DB =
     (DESCRIPTION =
       (ADDRESS = (PROTOCOL = TCP)(HOST = your.hostname.edu)(PORT = 1521))
       (CONNECT_DATA =
         (SERVICE_NAME = XEPDB1)
       )
     )
   ```

3. **Test with `sqlplus` or `tnsping`**  
   Example:
   ```
   sqlplus your_username@DWHDB_DB
   ```

If you can connect via `sqlplus`, HoonyTools will work too.

📥 [Download Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html)

---

## 🚀 How to Launch

Simply double-click `HoonyTools.pyw` to launch the application.

This file opens without a terminal window and starts the GUI immediately.

---

### 🏁 First-Time Run

On first launch:

- You’ll be prompted to **create `SCFF/` and `MIS/` folders** if they don’t exist
- These folders are used to manage incoming SCFF ZIP files and MIS `.dat` inputs

✅ These directories **do not affect production** — HoonyTools only uploads to your authorized DWH schema.

---

### 🧭 GUI Usage

Once launched, the GUI gives access to all tools via an intuitive interface:

- Load SCFF and MIS files
- Clean tables or delete old records
- Load Excel and CSV files
- Load SQL queries as views
- View console logs and abort operations gracefully

You can run as often as needed — no admin rights or elevated privileges required.

---

## 🛠 Available Tools

- **SCFF Loader**  
  Load SCFF TXT files into Oracle from `SCFF/SCFF_Data/<ACYR>/Latest`.  
  Automatically converts folder names like `2324` into `2023` ACYR to align with `STVTERM_ACYR_CODE` used in Banner.  
  Prompts for DWH password once and saves it.

- **MIS Loader**  
  Load MIS `.dat` files from the `MIS/` folder into Oracle. Prompts for DWH login.  
  Supports dynamic layout parsing and full rollback on failure.

- **SQL View Loader**  
  Instantly create Oracle views from SQL files placed in the `views/` folder.  
  Useful for versioned Banner views or department-specific logic. Supports both user schema and DWH.

- **Excel/CSV Loader**  
  Load Excel or CSV files into Oracle from a local file picker.  
  Auto-maps column headers and preserves datatypes.

- **SCFF Extractor**  
  Extract SCFF ZIP files from `SCFF/Downloads/` into the correct `SCFF_Data/<ACYR>/Latest` folder.

- **Table Cleanup**  
  Selectively delete rows or drop tables from your Oracle schema.  
  Works with user schema or DWH, depending on the tool settings.

- **SCFF/MIS Cleanup**  
  Targeted deletion based on `ACYR` (SCFF) or `TERM` (MIS) within DWH schema.  
  Only affects rows, not entire tables.


### 📈 Automatic Indexing (PIDM / TERM / STUDENT_ID)

To optimize query performance, **HoonyTools automatically creates indexes** on commonly used key columns — if they exist in your uploaded data.

#### ✅ Indexable Columns by Tool

| Loader         | Columns Automatically Indexed                                          |
|----------------|------------------------------------------------------------------------|
| SCFF Loader    | `STUDENT_ID`, `ACYR`                                                   |
| MIS Loader     | `GI90_RECORD_CODE`, `GI01_DISTRICT_COLLEGE_ID`, `GI03_TERM_ID`        |
| Excel/CSV      | `PIDM`, `TERM`, `STUDENT_ID`                                           |

Indexes are created after the table is generated. If the table already exists, HoonyTools safely skips duplicate index creation.

> 💡 **Tip:** Make sure your column headers in Excel or CSV match exactly (e.g., `PIDM`, not `Pidm`) to benefit from automatic indexing.

If Oracle cannot create the index due to a key size limit (e.g., `VARCHAR2(4000)`), HoonyTools automatically shortens the column length for these keys. A warning will be logged if indexing still fails.

---

## 📌 Notes for Users

- Ensure your **Oracle Instant Client** is properly installed and configured (see setup section above).
- You must be connected to your institution’s network or VPN if the Oracle database is not publicly accessible.
- All tools require a valid Oracle **DSN (Data Source Name)** such as `DWHDB_DB`. You may define your own DSN in `tnsnames.ora` to point to your organization’s database.
- The first time you run a tool that connects to Oracle, you will be prompted for your **username, password, and DSN**.  
  A **"Save password"** checkbox is available in the login popup. If checked, your credentials will be saved in `libs/config.ini` for future use. If unchecked, the login prompt will appear every time.
- **Use caution when working with production databases**. Certain tools (e.g., SCFF and MIS loaders, Table Cleanup) can delete and overwrite data.
- For best results, always review your files before running a loader, and monitor the logging window for any errors or warnings.

> 🧠 **Note:** This toolset interacts directly with the Oracle Data Warehouse (DWH). Ensure you understand the impact of any actions, particularly when loading SCFF/MIS files or using cleanup tools.

💡 **Tip:** To reset your saved DWH credentials (e.g., if the DSN or password changes), simply delete the `libs/config.ini` file.  
The next time you launch a DWH-related tool, HoonyTools will prompt you to enter new login information and ask whether to save it again.

---

## 📖 Documentation & Roadmap

- For upcoming features, enhancements, and community-driven ideas, see [ROADMAP.md](ROADMAP.md).
- To report bugs or suggest improvements, please open an issue on GitHub or reach out to the maintainer directly through the contact info listed at the bottom of this README.

---

## 🚟 Notes for Developers

This section documents key implementation details, platform-specific workarounds, and lessons learned during the development of HoonyTools. It is intended to help future contributors maintain stability across platforms and understand why certain design choices were made.

Although HoonyTools now runs as a Python-based `.pyw` app by default, these EXE-specific workarounds remain valuable for any future signed `.exe` packaging (e.g., with PyInstaller + certificate signing).

---

### 🪟 Entry #1: Taskbar Icon Ownership and PyInstaller + Tkinter on Windows

A detailed breakdown of how we ensure HoonyTools shows the correct custom icon in the taskbar when bundled as an `.exe`.

#### Key Findings

- **Taskbar icon is owned by the *first visible Tkinter window*.**  
  We must call `Tk()` and make it visible **before** any splash screens or login prompts. Otherwise, the icon becomes permanently associated with the wrong window.
  
- **Destroying the original `Tk()` root window early (e.g., before GUI loads) causes the taskbar icon to revert to the default feather icon.**  
  To prevent this, we create `hidden_root = Tk()` and **never destroy it** until full exit.

- **`SetCurrentProcessExplicitAppUserModelID()` is required** to reliably attach the embedded `.ico` to the taskbar icon when bundled with PyInstaller.

- **Splash screens and modal popups cannot claim taskbar ownership.**  
  Only the main `Toplevel` window can do so, and it must be shown first.

---

#### Implementation Details

```python
# Inside launcher_gui.py

hidden_root = Tk()
hidden_root.withdraw()  # Keep root hidden but alive to retain taskbar icon

root = Toplevel(hidden_root)  # Main GUI window attached to hidden_root

# Set custom icon and app ID (required for taskbar ownership)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hoonywise.hoonytools")
root.iconbitmap(default=icon_ico_path)  # .ico file embedded via PyInstaller
```

#### What Breaks It

Creating a splash screen or login window before showing the main GUI

Destroying the original Tk() instance before Toplevel is displayed

Using PhotoImage(...) without keeping a reference
(e.g., forgetting root.icon_img = icon_img) leads to silent icon failure

#### Safe Exit Pattern

```
def safe_exit():
    global is_gui_running
    is_gui_running = False
    try:
        root.destroy()
    except Exception:
        pass
    try:
        hidden_root.destroy()
    except Exception:
        pass
```

---

### 🐞 Entry #2: MIS Loader Crash (FA/SF files) and Tkinter Thread Violation

#### What Happened

When loading FA or SF `.dat` files using the MIS Loader, HoonyTools crashed with errors like:

> ❌ `Login prompt must be called from the main thread.`  
> ❌ `Toplevel()` window creation failed due to threading issues

This happened because the loader attempted to open a Tkinter login window (`Toplevel`) inside a background thread — which is not allowed by Tkinter on Windows.

#### What We Learned

- **Tkinter GUI elements must always be created from the main thread.**
- **`Toplevel()` windows used in login prompts must be attached to the `_default_root`.**
- Background loaders like `run_mis_loader()` must receive the Oracle connection object **after login**, not initiate the login themselves.

#### Fix Implemented

- Moved the call to `get_db_connection()` into the **main thread** (within `run_selected()` in `launcher_gui.pyw`).
- The returned `conn` object is passed into `run_mis_loader(existing_conn=conn)` inside the thread — solving the crash.

---

More developer entries will be added here as we identify new platform-specific quirks, architecture patterns, or tricky implementation areas.

---

## 🧑‍💼 Maintainer

Created and maintained by: [@hoonywise](https://github.com/hoonywise)  
Contact: [hoonywise@proton.me](mailto:hoonywise@proton.me)

For questions, suggestions, or contributions, feel free to reach out or open a GitHub issue.

---

## 📜 License

HoonyTools is free for individual, non-commercial use.  
Use across departments or organizations may require a license.

📩 **For enterprise use or questions, contact:**  
**[hoonywise@proton.me](mailto:hoonywise@proton.me)**

For full terms, see [LICENSE.md](LICENSE.md).
