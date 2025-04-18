from pathlib import Path
import sys

def _get_pyinstaller_temp_path():
    return Path(sys._MEIPASS)

# Logos/splash loaded from bundled temp (_MEIPASS)
ASSETS_PATH = _get_pyinstaller_temp_path() if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent

# ✅ SCFF + MIS folders will live next to HoonyTools.exe or launcher_gui.pyw
if getattr(sys, 'frozen', False):
    PROJECT_PATH = Path(sys.executable).parent
else:
    PROJECT_PATH = Path(__file__).resolve().parent
