# SCFF Data Loader Script
import os
import zipfile
import shutil
from datetime import datetime
import re
from pathlib import Path
import logging

if __name__ != '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
from config import PROJECT_PATH as base_path
downloads_path = base_path / "SCFF" / "Downloads"
data_path = base_path / "SCFF" / "SCFF_Data"

logger = logging.getLogger(__name__)

# Step 1: Extract aid year and date from the ZIP file contents
def get_academic_year_and_date(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for name in zip_ref.namelist():
            match = re.search(r'_(\d{4})_(\d{6})', name)
            if match:
                return match.group(1), match.group(2)
    return 'unknown', '000000'

# Step 2: Ensure the folder structure exists
def ensure_folders(academic_year):
    year_path = data_path / academic_year
    latest_path = year_path / 'Latest'
    archive_path = year_path / 'Archive'
    os.makedirs(latest_path, exist_ok=True)
    os.makedirs(archive_path, exist_ok=True)
    return latest_path, archive_path

# Step 3: Check if the new data is newer than existing latest
def is_newer_version(latest_path, new_date):
    for file in os.listdir(latest_path):
        match = re.search(r'_(\d{6})\.txt$', file)
        if match and match.group(1) >= new_date:
            logger.info(f"Existing data version {match.group(1)} is the same or newer.")
            return False
    return True

# Step 4: Remove duplicate sets from Latest if already archived
def clean_latest_if_duplicated(latest_path, archive_path):
    latest_files = set(os.listdir(latest_path))
    archive_files = set(os.listdir(archive_path))
    if latest_files.issubset(archive_files):
        logger.info("Duplicate set found in Latest and Archive. Removing from Latest.")
        for file in latest_files:
            os.remove(os.path.join(latest_path, file))
        logger.info("Latest folder cleaned.")

# Step 5: Move old files to archive
def archive_old_files(latest_path, archive_path):
    clean_latest_if_duplicated(latest_path, archive_path)
    for file in os.listdir(latest_path):
        if os.path.exists(os.path.join(archive_path, file)):
            logger.info(f"File {file} already exists in archive. Skipping move.")
        else:
            shutil.move(os.path.join(latest_path, file), os.path.join(archive_path, file))
            logger.info(f"Archived: {file}")

# Step 6: Extract the latest SCFF ZIP file
def extract_latest_zip():
    zip_file = os.path.join(downloads_path, 'scff860.zip')
    if not os.path.exists(zip_file):
        logger.info("No SCFF ZIP file found in Downloads.")
        return

    academic_year, new_date = get_academic_year_and_date(zip_file)
    latest_path, archive_path = ensure_folders(academic_year)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_contents = zip_ref.namelist()
        txt_files_in_zip = [f for f in zip_contents if f.endswith('.txt')]

        latest_files = os.listdir(latest_path)
        extracted_any = False

        for file in txt_files_in_zip:
            filename = os.path.basename(file)
            target_path = os.path.join(latest_path, filename)

            # Replace if missing or older version exists
            match = re.search(r'_(\d{6})\.txt$', filename)
            if not match:
                continue
            zip_datestamp = match.group(1)

            existing = [f for f in latest_files if f.startswith(filename.split('_')[0])]
            existing_datestamps = [re.search(r'_(\d{6})\.txt$', f).group(1) for f in existing if re.search(r'_(\d{6})\.txt$', f)]
            should_extract = (
                filename not in latest_files or
                any(d < zip_datestamp for d in existing_datestamps)
            )

            if should_extract:
                # Archive old version if it exists
                for f in existing:
                    src = os.path.join(latest_path, f)
                    dst = os.path.join(archive_path, f)
                    if os.path.exists(src):
                        shutil.move(src, dst)
                        logger.info(f"Archived older version: {f} (if it already exists it will be overwritten)")
                    else:
                        logger.warning(f"⚠️ Tried to archive {f}, but it was already missing from Latest.")


                zip_ref.extract(file, latest_path)
                logger.info(f"Extracted: {filename}")
                extracted_any = True

        if extracted_any:
            logger.info(f"Extraction completed for aid year {academic_year} with datestamp {new_date}.")
        else:
            logger.info("No new files needed to be extracted. All files are already current.")

# Main process
def main():
    extract_latest_zip()
    logger.info("✅ SCFF extraction process finished.")

if __name__ == '__main__':
    main()
