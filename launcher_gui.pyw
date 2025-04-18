import tkinter as tk
from tkinter import scrolledtext, ttk
import tkinter.font as tkfont
import logging
import threading
from io import StringIO
import ctypes
import sys
from pathlib import Path
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item


# Dynamically add HoonyTools's parent to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # HoonyTools parent

# Add shared HoonyTools path manually
from config import PROJECT_PATH as base_path
from config import ASSETS_PATH
sys.path.append(str(base_path))

from libs import abort_manager
from loaders.excel_csv_loader import load_multiple_files
from loaders.sql_view_loader import run_sql_view_loader
from loaders.scff_data_loader import run_scff_loader
from loaders.mis_data_loader import run_mis_loader
from tools.table_cleanup_gui import drop_user_tables, delete_dwh_rows
from tools.scff_data_extractor import main as run_scff_extractor

should_abort = False
auto_scroll_enabled = True
is_gui_running = True

def validate_required_folders():
    from tkinter import messagebox
    required = [
        base_path / "SCFF" / "Downloads",
        base_path / "SCFF" / "SCFF_Data",
        base_path / "MIS"
    ]
    missing = [p for p in required if not p.exists()]

    if missing:
        msg = "⚠️ The following required folders are missing:\n\n" + \
              "\n".join(str(p) for p in missing) + \
              "\n\nWould you like to create them now?"

        confirm = messagebox.askyesno("Missing Folders", msg)
        if confirm:
            for folder in missing:
                folder.mkdir(parents=True, exist_ok=True)
                logging.info(f"📁 Created folder: {folder}")
            messagebox.showinfo("Folders Created", "✅ All missing folders have been created.")
        else:
            messagebox.showwarning("Setup Incomplete", "❌ Folders are required to run SCFF and MIS tools.\n\nPlease create them before continuing.")
            return False

    return True

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def abort_process():
    abort_manager.set_abort(True)
    logging.warning("⛔ Abort requested by user.")

def run_selected():
    global should_abort
    should_abort = False
    tool_name = selected_tool.get()
    log_text.delete(1.0, tk.END)
    status_light.config(text="⏳") 
    logging.info(f"🚀 Running: {tool_name}")

    def run_and_update_with_conn(conn):
        try:
            TOOLS[tool_name](conn)
        except Exception as e:
            logging.exception(f"❌ Error running {tool_name}: {e}")
        finally:
            status_light.config(text="🟢")

    if tool_name == "✅ Excel/CSV Loader":
        def threaded_excel():
            try:
                TOOLS[tool_name]()
            except Exception as e:
                logging.exception(f"❌ Error running {tool_name}: {e}")
            finally:
                status_light.config(text="🟢")

        threading.Thread(target=threaded_excel, daemon=True).start()
        return

    if tool_name == "🔒 SCFF Loader" or tool_name == "🔒 MIS Loader":
        from libs.oracle_db_connector import get_db_connection
        conn = get_db_connection(force_shared=True)
        if not conn:
            return
        threading.Thread(target=lambda: run_and_update_with_conn(conn), daemon=True).start()
        return

    # For everything else
    def run_and_update():
        try:
            if tool_name == "☑ SQL View Loader":
                TOOLS[tool_name](on_finish=lambda: status_light.config(text="🟢"))
            else:
                TOOLS[tool_name]()
                status_light.config(text="🟢")
        except Exception as e:
            logging.exception(f"❌ Error running {tool_name}: {e}")
            status_light.config(text="🟢")

    run_and_update()

def stream_logs():
    global is_gui_running
    if not is_gui_running or not log_text.winfo_exists():
        return  # Stop logging loop if GUI is closed

    try:
        text = log_stream.getvalue()
        log_text.insert(tk.END, text)

        if auto_scroll_enabled:
            log_text.see(tk.END)

        log_stream.truncate(0)
        log_stream.seek(0)

        from libs.oracle_db_connector import process_queued_errors
        process_queued_errors(root)

    except tk.TclError:
        return  # Window or widget was destroyed

    log_text.after(500, stream_logs)


def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    center_window(splash, 420, 260)
    splash.attributes('-alpha', 0.0)

    # === HoonyTools Logo + Title ===
    try:
        hoony_logo_path = ASSETS_PATH / "assets" / "hoonywise_300.png"
        hoony_img = Image.open(hoony_logo_path).resize((36, 36))
        hoony_logo = ImageTk.PhotoImage(hoony_img)

        logo_title_frame = tk.Frame(splash)
        logo_title_frame.pack(pady=(40, 10))

        tk.Label(logo_title_frame, image=hoony_logo).pack(side="left", padx=(0, 10))
        tk.Label(logo_title_frame, text="HoonyTools Launcher", font=("Arial", 16, "bold")).pack(side="left")

        splash.hoony_logo = hoony_logo  # Prevent garbage collection
    except:
        tk.Label(splash, text="HoonyTools Launcher", font=("Arial", 18, "bold")).pack(pady=(40, 10))

    # === Created by hoonywise ===
    creator_label = tk.Label(splash, text="Created by hoonywise", font=("Arial", 10, "italic"), fg="#444444")
    creator_label.pack(side="bottom", pady=20)
    license_label = tk.Label(splash, text="For enterprise use, contact: hoonywise@proton.me", font=("Arial", 8, "italic"), fg="#444444")
    license_label.pack(side="bottom", pady=(0, 5))    
    creator_label.attributes = {"opacity_step": 0}

    def fade_in(alpha=0.0):
        if alpha < 1.0:
            splash.attributes('-alpha', alpha)
            splash.after(30, lambda: fade_in(alpha + 0.05))
        else:
            splash.after(3000, fade_out)  # hold full splash (logo + labels) for 3s

    def fade_out(alpha=1.0):
        if alpha > 0.0:
            splash.attributes('-alpha', alpha)
            splash.after(14, lambda: fade_out(alpha - 0.7))
        else:
            splash.destroy()
            
    fade_in()
    splash.mainloop()

def launch_tool_gui():
    from libs.oracle_db_connector import prompt_credentials
    from libs import session  # 👈 NEW


    
    global root, selected_tool, log_text, log_stream, status_light

    hidden_root = tk.Tk()
    hidden_root.withdraw()  # Hide it immediately
    
    # 👇 Taskbar ownership
    root = tk.Toplevel(hidden_root)
    root.protocol("WM_DELETE_WINDOW", hidden_root.quit)

    # Set Windows AppUserModelID for taskbar icon
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hoonywise.hoonytools")
            icon_ico_path = ASSETS_PATH / "assets" / "hoonywise_gui.ico"
            root.iconbitmap(default=icon_ico_path)
        except Exception as e:
            print(f"⚠️ Failed to set taskbar icon: {e}")

    # 🪄 Position tiny window exactly behind login popup
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    login_width = 330
    login_height = 150
    x = int((screen_width / 2) - (login_width / 2)) + 16  # Nudge right
    y = int((screen_height / 2) - (login_height / 2))
    root.geometry(f"1x1+{x}+{y}")
    root.update()
    root.deiconify()

    # 4️⃣ 🔐 Prompt for login
    session.stored_credentials = prompt_credentials()
    if not session.stored_credentials:
        root.destroy()
        hidden_root.destroy()
        return
    
    # ✅ After login success
    center_window(root, 750, 650)  # Resize to full GUI
    root.title("HoonyTools Launcher")

    # ✅ Set GUI icon (.ico for taskbar)
    icon_ico_path = ASSETS_PATH / "assets" / "hoonywise_gui.ico"
    root.iconbitmap(default=icon_ico_path)

    # ✅ Set window icon (.png for title bar)
    icon_path = ASSETS_PATH / "assets" / "hoonywise_300.png"
    icon_img = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, icon_img)
    root.icon_img = icon_img  # Prevents garbage collection

    # === Load Logo Assets ===
    assets_path = base_path / "assets"
    
    tool_select_frame = tk.Frame(root)
    tool_select_frame.pack(pady=(10, 10))

    tk.Label(
        tool_select_frame, 
        text="Select Tool:",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 10))
    
    legend_frame = tk.Frame(root)
    legend_frame.pack(fill="x", padx=10)

    tk.Label(
        legend_frame,
        text="☑ = User/DWH   |   🔒 = DWH only   |   📁 = Local only",
        font=("Arial", 10),
        anchor="w",  # align left
        justify="left"
    ).pack() 

    selected_tool = tk.StringVar()
    tool_menu = ttk.Combobox(tool_select_frame, textvariable=selected_tool, values=list(TOOLS.keys()), font=("Arial", 11), state="readonly", width=22)
    tool_menu.pack(side="left")

    # Optional: pre-select the first item
    tool_menu.current(0)

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    tk.Button(btn_frame, text="Run", width=10, command=lambda: run_selected()).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Abort", width=10, command=abort_process).pack(side="left", padx=5)

    def safe_exit():
        global is_gui_running
        is_gui_running = False
        try:
            root.destroy()
        except Exception:
            pass
        # ❌ DO NOT destroy hidden_root — let the process exit handle it
        sys.exit()

    tk.Button(btn_frame, text="Exit", width=10, command=safe_exit).pack(side="left", padx=5)

    log_text = scrolledtext.ScrolledText(root, width=100, height=25)  # ⬆️ taller only
    log_text.pack(padx=10, pady=(5, 5), fill="both", expand=True)
    
    # --- Status Bar (bottom left + busy indicator on right) ---
    tk.Frame(root, height=1, bg="#ccc").pack(fill="x", padx=10)
    status_bar = tk.Frame(root)
    status_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 5))

    tk.Label(
        status_bar,
        text=f"Logged in as: {session.stored_credentials['username']} @ {session.stored_credentials['dsn']}",
        font=("Arial", 8),
        anchor="w",
        justify="left"
    ).pack(side="left")

    # 🟢/🔴 Busy indicator (right side)
    status_light = tk.Label(
        status_bar,
        text="🟢",  # default: idle
        font=("Arial", 12)
    )
    status_light.pack(side="right", padx=10)

    def on_scroll(*args):
        global auto_scroll_enabled
        if float(log_text.yview()[1]) >= 0.999:
            auto_scroll_enabled = True
        else:
            auto_scroll_enabled = False

    log_text.config(yscrollcommand=lambda *args: [on_scroll(*args), log_text.yview_moveto(args[0])])

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().handlers = [handler]
    logging.getLogger().setLevel(logging.INFO)

    stream_logs()
    
    # ✅ Validate after GUI + log area are ready
    if not validate_required_folders():
        root.destroy()
        return
    
    def setup_tray_icon():
        def on_exit(icon, item):
            icon.stop()
            root.quit()

        tray_icon_path = ASSETS_PATH / "assets" / "hoonywise_32x32.png"
        if tray_icon_path.exists():
            tray_img = Image.open(tray_icon_path)
            tray_icon = pystray.Icon("HoonyTools", tray_img, "HoonyTools", menu=(item("Exit", on_exit),))
            tray_icon.run()

    # 🧠 Start it in the background so GUI stays responsive
    threading.Thread(target=setup_tray_icon, daemon=True).start()    
        
    root.mainloop()

TOOLS = {    
    "☑ Excel/CSV Loader": load_multiple_files,
    "☑ Table/View Dropper": drop_user_tables,
    "☑ SQL View Loader": run_sql_view_loader,
    "📁 SCFF Extractor": run_scff_extractor,
    "🔒 SCFF Loader": run_scff_loader,        # accepts optional conn
    "🔒 SCFF Record Cleanup": lambda: delete_dwh_rows(
        "SCFF_%", "ACYR", "Enter ACYR to delete from selected SCFF tables:", root
    ),
    "🔒 MIS Loader": run_mis_loader,          # accepts optional conn
    "🔒 MIS Record Cleanup": lambda: delete_dwh_rows(
        "MIS_%_IN", "TERM", "Enter TERM to delete from selected MIS tables:", root
    ),
}

if __name__ == "__main__":
    show_splash()
    launch_tool_gui()
