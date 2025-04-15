import sys
import getpass
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "libs" / "config.ini"
FORCE_OVERWRITE = "--force" in sys.argv

if CONFIG_PATH.exists() and not FORCE_OVERWRITE:
    print("⚠️  config.ini already exists.")
    print("💡 Re-run with '--force' to overwrite it:")
    print("    python setup_config.py --force")
    exit()

print("🔐 Setup: DWH Connection Configuration")
print("→ Schema: dwh")
print("→ DSN: DWHDB_DB")
print()

password = getpass.getpass("Enter your DWH Oracle password: ").strip()

if not password:
    print("❌ Password is required. Exiting.")
    exit()

config_text = f"""[dwh]
username = dwh
password = {password}
dsn = DWHDB_DB
"""

CONFIG_PATH.write_text(config_text)
print(f"✅ config.ini created at: {CONFIG_PATH}")
print("\n📌 You can re-run this script anytime to reset your password.")

