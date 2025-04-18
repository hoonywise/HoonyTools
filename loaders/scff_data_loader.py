# SCFF Data Loader with Datestamp Check and Abort Rollback
import os
import oracledb
import pandas as pd
from datetime import datetime
import re
import logging
from libs.oracle_db_connector import get_db_connection
from pathlib import Path
from libs import abort_manager
from libs.table_utils import create_index_if_columns_exist

# Configuration
from config import PROJECT_PATH as base_path
data_path = base_path / "SCFF" / "SCFF_Data"

# Logging setup
logger = logging.getLogger(__name__)

# Step 1: Clean column names to be Oracle compatible
def clean_column_names(df):
    df.columns = [col.strip().replace(' ', '_').replace('-', '_').replace('.', '_').upper() for col in df.columns]
    return df

# Step 2: Convert all values to strings
def convert_to_string(df):
    return df.astype(str).fillna('')

# Step 3: Extract datestamp from filename
def extract_datestamp(filename):
    match = re.search(r'_(\d{6})\.txt$', filename)
    return match.group(1) if match else None

# Step 4: Check if table exists
def table_exists(cursor, table_name):
    try:
        cursor.execute(f"SELECT table_name FROM all_tables WHERE table_name = '{table_name}' AND owner = 'DWH'")
        return cursor.fetchone() is not None
    except oracledb.DatabaseError:
        return False

# Step 5: Check if the datestamp column exists
def column_exists(cursor, table_name, column_name):
    try:
        cursor.execute(f"SELECT column_name FROM all_tab_columns WHERE table_name = '{table_name}' AND column_name = '{column_name}' AND owner = 'DWH'")
        return cursor.fetchone() is not None
    except oracledb.DatabaseError:
        return False

# Step 6: Check if new datestamp is greater than existing
def is_newer_datestamp(cursor, table_name, new_datestamp):
    try:
        if not column_exists(cursor, table_name, 'DATESTAMP'):
            return True  # No datestamp column, treat as new
        cursor.execute(f'SELECT MAX(DATESTAMP) FROM DWH.{table_name.upper()}')
        result = cursor.fetchone()
        if result and result[0] and int(new_datestamp) <= int(result[0]):
            return False
        return True
    except oracledb.DatabaseError as e:
        logger.error(f'Error checking datestamp for {table_name}: {e}')
        return True

# Load data to DWHDB with Datestamp Check
def load_data_to_db(table_name, acyr, datestamp, df, conn, cursor):
    df = clean_column_names(df)
    df = convert_to_string(df)
    df['ACYR'] = acyr
    df['DATESTAMP'] = datestamp
    table_name = f'SCFF_{table_name}'
    table_needs_create = not table_exists(cursor, table_name)
    if table_needs_create:
        create_table_query = f'CREATE TABLE DWH.{table_name.upper()} ({", ".join([
            f'"{col}" VARCHAR2(9)' if col.upper() == "STUDENT_ID" else
            f'"{col}" VARCHAR2(4)' if col.upper() == "ACYR" else
            f'"{col}" VARCHAR2(4000)' for col in df.columns
        ])})'
        try:
            cursor.execute(create_table_query)
            cursor.execute(f'GRANT SELECT ON DWH.{table_name.upper()} TO PUBLIC')
            abort_manager.register_created_table(table_name)
            logger.info(f'Table {table_name} created and granted SELECT to PUBLIC.')
        except oracledb.DatabaseError as e:
            logger.error(f'Error creating table {table_name}: {e}')

    # ✅ Always attempt to create index (safely handles duplicates)
    create_index_if_columns_exist(cursor, "DWH", table_name, ["STUDENT_ID", "ACYR"])

    delete_query = f'DELETE FROM DWH.{table_name.upper()} WHERE ACYR = :1'
    cursor.execute(delete_query, [acyr])
    logger.info(f'Deleted existing records for ACYR {acyr} from {table_name}.')

    insert_query = f'INSERT INTO DWH.{table_name.upper()} ({', '.join([f'"{col}"' for col in df.columns])}) VALUES ({', '.join([f':{i+1}' for i in range(len(df.columns))])})'
    for _, row in df.iterrows():
        if abort_manager.should_abort:
            abort_manager.cleanup_on_abort(conn, cursor)
            return False
        try:
            cursor.execute(insert_query, tuple(row))
        except oracledb.DatabaseError as e:
            logger.error(f'Failed to insert row into {table_name}: {e}')

    logger.info(f'Loaded {len(df)} rows into {table_name} after deleting old records.')
    return True

# Main data loading process
def process_latest_files(latest_path, acyr, conn, cursor):
    for file in os.listdir(latest_path):
        if abort_manager.should_abort:
            abort_manager.cleanup_on_abort(conn, cursor)
            return False
        if file.endswith('.txt'):
            file_path = os.path.join(latest_path, file)
            table_name = file.split('_')[0]
            datestamp = extract_datestamp(file)
            logger.info(f'Processing {file} into table SCFF_{table_name} with datestamp {datestamp}...')
            try:
                df = pd.read_csv(file_path, sep="|", dtype=str)
                df = clean_column_names(df)
                df = convert_to_string(df)
                if not load_data_to_db(table_name, acyr, datestamp, df, conn, cursor):
                    return False
            except Exception as e:
                logger.error(f'Error processing {file}: {e}')
    return True


def run_scff_loader(existing_conn=None):
    conn = existing_conn or get_db_connection(force_shared=True)
    if not conn:
        logger.error("❌ Could not connect to Oracle.")
        return
    cursor = conn.cursor()

    from libs import abort_manager
    abort_manager.reset()

    academic_years = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    for academic_year in academic_years:
        if abort_manager.should_abort:
            logger.warning("⏹️ SCFF Loader aborted by user.")
            break

        try:
            acyr = str(2000 + int(academic_year[:2]))
        except Exception:
            logger.warning(f"⚠️ Could not derive ACYR from folder name '{academic_year}'. Skipping.")
            continue

        latest_path = os.path.join(data_path, academic_year, 'Latest')
        if os.path.exists(latest_path):
            logger.info(f'Loading data from Latest folder for academic year: {academic_year}, derived ACYR: {acyr}')
            success = process_latest_files(latest_path, acyr, conn, cursor)
            if success:
                conn.commit()
                logger.info(f"✅ Committed records for ACYR {acyr}")
            else:
                logger.warning(f"⏪ Rolled back records for ACYR {acyr}")
                break
        else:
            logger.error(f'No Latest folder found for academic year: {academic_year}')

    try:
        cursor.close()
    except Exception as e:
        if "DPY-1001" not in str(e):
            logger.warning(f"⚠️ Failed to close cursor: {e}")

    try:
        conn.close()
    except Exception as e:
        if "DPY-1001" not in str(e):
            logger.warning(f"⚠️ Failed to close connection: {e}")
