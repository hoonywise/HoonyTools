import logging

logger = logging.getLogger(__name__)

def create_index_if_columns_exist(cursor, schema, table_name, columns):
    """
    Creates an index on the specified columns if they exist in the table.
    The index name is auto-generated as <TABLE>_<COL1>_<COL2>_IDX.
    If the index already exists, it skips creation without error.
    """
    try:
        cursor.execute("""
            SELECT column_name 
            FROM all_tab_columns 
            WHERE table_name = :1 AND owner = :2
        """, [table_name.upper(), schema.upper()])
        existing_cols = set(row[0] for row in cursor.fetchall())

        index_cols = [col.upper() for col in columns if col.upper() in existing_cols]
        if not index_cols:
            logger.info(f"ℹ️ Skipping index creation: none of {columns} found in {schema}.{table_name}")
            return

        index_name = f"{table_name.upper()}_" + "_".join(index_cols) + "_IDX"
        index_sql = f'CREATE INDEX {index_name} ON {schema}.{table_name.upper()} ({", ".join(index_cols)})'

        try:
            cursor.execute(index_sql)
            logger.info(f"⚡ Created index {index_name} on {schema}.{table_name} for columns {index_cols}")
        except Exception as inner_e:
            error_str = str(inner_e)
            if "ORA-01408" in error_str:
                logger.info(f"ℹ️ Index on same column(s) already exists on {schema}.{table_name}. Skipping.")
            elif "ORA-00955" in error_str:
                logger.info(f"ℹ️ Index name {index_name} already exists on {schema}.{table_name}. Skipping.")
            elif "ORA-01450" in error_str:
                logger.warning(f"⚠️ Cannot create index {index_name} — max key length exceeded. Consider reducing column size.")
            elif "ORA-00904" in error_str:
                logger.warning(f"⚠️ Invalid column name used in index {index_name}. Check column spelling and case.")
            else:
                logger.warning(f"⚠️ Failed to create index {index_name} on {schema}.{table_name}: {inner_e}")

    except Exception as e:
        logger.warning(f"⚠️ Failed index logic on {schema}.{table_name}: {e}")
