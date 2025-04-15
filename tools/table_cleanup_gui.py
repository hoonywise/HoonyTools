import sys
from pathlib import Path
from config import PROJECT_PATH as BASE_PATH
import oracledb
import logging
from tkinter import Toplevel, Label, Checkbutton, IntVar, Button, messagebox, simpledialog, Frame, Canvas, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH
from libs.oracle_db_connector import get_db_connection

logger = logging.getLogger(__name__)

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")
    
def prompt_schema_choice():
    result = {"choice": None}

    def select_user():
        result["choice"] = "user"
        win.destroy()

    def select_dwh():
        result["choice"] = "dwh"
        win.destroy()

    def cancel():
        result["choice"] = None
        win.destroy()

    win = Toplevel()
    win.title("Select Schema Scope")
    center_window(win, 300, 140)
    win.resizable(False, False)

    Label(win, text="Drop from which schema?", font=("Arial", 11, "bold")).pack(pady=(15, 10))

    btn_frame = Frame(win)
    btn_frame.pack(pady=5)

    b1 = Button(btn_frame, text="User Schema", width=12, command=select_user)
    b2 = Button(btn_frame, text="DWH Schema", width=12, command=select_dwh)
    b3 = Button(btn_frame, text="Cancel", width=12, command=cancel)

    b1.pack(side="left", padx=5)
    b2.pack(side="left", padx=5)
    b3.pack(side="left", padx=5)

    # Enable keyboard focus
    b1.focus()
    b1.configure(takefocus=True)
    b2.configure(takefocus=True)
    b3.configure(takefocus=True)
    win.grab_set()
    win.wait_window()

    return result["choice"]    

def select_tables_gui(tables, title="Select tables to delete from your schema:"):
    selected = []

    def on_submit():
        for table, var in vars_.items():
            if var.get():
                selected.append(table)
        window.destroy()

    def on_cancel():
        window.destroy()

    window = Toplevel()
    window.title(title)
    center_window(window, 500, 600)

    Label(window, text=title).pack(pady=5)

    # Top-aligned buttons
    btn_frame = Frame(window)
    btn_frame.pack(pady=(0, 10))
    Button(btn_frame, text="OK", width=10, command=on_submit).pack(side="left", padx=20)
    Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=20)

    # Scrollable canvas for table list
    canvas = Canvas(window)
    scrollbar = Scrollbar(window, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # 🖱️ Enable mouse scrolling inside the canvas
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    vars_ = {}
    for table in tables:
        var = IntVar()
        chk = Checkbutton(scrollable_frame, text=table, variable=var)
        chk.pack(anchor="w")
        vars_[table] = var

    window.grab_set()
    window.wait_window()
    return selected

def drop_user_tables():
    schema_choice = prompt_schema_choice()
    if schema_choice is None:
        return

    conn = get_db_connection(force_shared=(schema_choice == "dwh"))
    if not conn:
        logger.error("❌ Failed to connect.")
        return

    schema = "DWH" if schema_choice == "dwh" else conn.username.upper()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT object_name FROM all_objects 
        WHERE owner = :owner 
        AND object_type IN ('TABLE', 'VIEW') 
        ORDER BY object_name
    """, [schema])
    objects = [row[0] for row in cursor.fetchall()]

    if not objects:
        messagebox.showinfo("No Objects", f"No tables or views found in schema {schema}")
        return

    selected = select_tables_gui(objects, f"Select tables/views to drop from schema: {schema}")
    if not selected:
        messagebox.showinfo("Cancelled", "No objects selected.")
        return

    if not messagebox.askyesno("Confirm", f"Drop {len(selected)} object(s) from schema {schema}?"):
        return

    for obj in selected:
        try:
            cursor.execute(f'DROP TABLE "{schema}"."{obj}" PURGE')
            logger.info(f"🗑️ Dropped table: {schema}.{obj}")
        except oracledb.DatabaseError as e:
            if "ORA-00942" in str(e) or "ORA-00955" in str(e):
                try:
                    cursor.execute(f'DROP VIEW "{schema}"."{obj}"')
                    logger.info(f"🗑️ Dropped view: {schema}.{obj}")
                except Exception as e2:
                    logger.warning(f"⚠️ Could not drop {obj} as view: {e2}")
            else:
                logger.warning(f"⚠️ Could not drop {obj}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Done", "✅ Cleanup complete.")
    logger.info("✅ Cleanup complete.")

def delete_dwh_rows(table_filter, label, prompt_label, parent_window=None):
    conn = get_db_connection(force_shared=True)
    if not conn:
        logger.error("❌ Failed to connect to DWH.")
        return

    schema = "DWH"
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM all_tables WHERE owner = :owner AND table_name LIKE :filter ORDER BY table_name", [schema, table_filter])
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        messagebox.showinfo("No Tables", f"No matching tables found in schema {schema}")
        return

    selected = select_tables_gui(tables, f"Select {schema} tables to delete rows from:")
    if not selected:
        messagebox.showinfo("Cancelled", "No tables selected.")
        return

    # Thread-safe input dialog with optional parent window
    def ask_string_threadsafe(title, prompt, parent=None):
        import threading, queue, tkinter as tk
        q = queue.Queue()

        def ask():
            def submit():
                val = entry.get().strip()
                q.put(val)
                win.destroy()

            def cancel():
                q.put(None)
                win.destroy()

            win = tk.Toplevel(parent)
            win.title(title)
            center_window(win, 350, 120)
            win.resizable(False, False)

            tk.Label(win, text=prompt).pack(pady=(15, 5))
            entry = tk.Entry(win, width=30)
            entry.pack(pady=5)
            entry.focus()  # ✅ Autofocus

            btn_frame = tk.Frame(win)
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="OK", width=10, command=submit).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancel", width=10, command=cancel).pack(side="left", padx=5)

            win.bind("<Return>", lambda event: submit())  # ✅ Enter to submit
            win.grab_set()
            win.wait_window()

        if threading.current_thread() is threading.main_thread():
            ask()
        else:
            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.after(0, ask)
            while q.empty():
                temp_root.update()
            temp_root.destroy()

        return q.get()

    value = ask_string_threadsafe(f"Enter {label}", prompt_label, parent=parent_window)

    if not value:
        messagebox.showwarning("Missing Input", f"{label} is required.")
        return

    if not messagebox.askyesno("Confirm", f"Delete rows from {len(selected)} tables where {label} = '{value}'?"):
        return

    for table in selected:
        try:
            column = "AIDY" if table.startswith("SCFF_") else "GI03_TERM_ID"
            cursor.execute(f'DELETE FROM DWH."{table}" WHERE {column} = :1', [value])
            logger.info(f"🧹 Deleted from {table} where {column} = {value}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete from {table}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Done", f"✅ Deleted rows where {label} = {value}")
    logger.info("✅ Row deletion complete.")
