import os
import csv
import re
import csv
import glob
import os
import sys
from pathlib import Path
from datetime import datetime, date

def get_log_files_in_date_range(base_pattern: str, 
                                start_date_str: str, 
                                end_date_str: str) -> list[str]:
    """
    Finds log files from a glob pattern that fall within a date range.

    Args:
        base_pattern: The glob pattern to search (e.g., 'Z:/.../*.txt').
        start_date_str: The start date in 'YYYY-MM-DD' format (inclusive).
        end_date_str: The end date in 'YYYY-MM-DD' format (inclusive).

    Returns:
        A list of file paths that match the criteria.
    """
    
    # --- 1. Define Date Range ---
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError as e:
        print(f"Error: Invalid date format. Please use YYYY-MM-DD. Details: {e}", file=sys.stderr)
        return []

    print(f"Filtering for dates: {start_date} to {end_date}\n")

    # --- 2. Get ALL files matching the pattern ---
    # This is your original line of code
    all_log_files = glob.glob(base_pattern)
    
    if not all_log_files:
        print(f"Warning: glob pattern '{base_pattern}' found 0 files.", file=sys.stderr)
        return []

    # --- 3. Filter the results ---
    filtered_log_files = []
    
    for file_path in all_log_files:
        try:
            # We need to extract the date string 'YYYY-MM-DD' from the path.
            # os.path.dirname(file_path) -> 'Z:/MACHINE/Analysis/2025-10-15/03'
            # os.path.dirname(...) -> 'Z:/MACHINE/Analysis/2025-10-15'
            # os.path.basename(...) -> '2025-10-15'
            
            date_str = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            
            # Convert the folder name to a date object
            current_date = date.fromisoformat(date_str)
            
            # The core logic: check if the date is within the desired range
            if start_date <= current_date <= end_date:
                filtered_log_files.append(file_path)
                
        except ValueError:
            # This handles cases where a file path matches the glob
            # but the folder name isn't a valid date (e.g., 'ABCD-12-34')
            # We simply ignore that file.
            continue
            
    return filtered_log_files

def get_value_from_log(file_content: str, key: str) -> str:
    for line in file_content.splitlines():
        parts = line.split('=', 1)
        if len(parts) == 2:
            found_key = parts[0].strip()
            if found_key == key:
                value = parts[1].strip()
                return value
    return "Value not found"

def main():
    # 1. Set your desired date range
    START_DATE = "2026-01-05" # "2025-10-10"
    END_DATE = "2026-01-09"

    # 2. This is your original glob pattern
    #    Note: Use forward slashes '/'.
    LOG_PATTERN = 'Z:/MACHINE/Analysis/????-??-??/??/*.txt'
    # log_files = glob.glob('Z:/MACHINE/Analysis/????-??-??/??/*.txt')
    csv_output_path = 'tim_usage_analysis_' + START_DATE + '_' + END_DATE + '.csv'
    
    log_files = get_log_files_in_date_range(LOG_PATTERN, START_DATE, END_DATE)

    if not log_files:
        print("No .txt log files found in any 'yyyy-mm-dd' subdirectories.")
        return

    print(f"Found {len(log_files)} log file(s) to process.")

    keys_to_find = [
        "TIME_START_CLIENT",
        "PRODUCT",
        "SKU",
        "PN",
        "SN",
        "PROCESS",
        "DIAG",
        "TESTER_TYPE",
        "FIXTURE",
        "TestTime",
        "TestStatus",
        "TestErrorCode",
        "TestErrorMessage",
        "CoreErrorCode",
        "CoreErrorMessage",
        "IMAGE_VBIOS",
        "IMAGE_CX8",
        "CX8_VERSION",
        "PCIE_VERSION",
        "BASEOS_VERSION",
        "OS_UPDATE",
        "GOLDEN_FILE",
        "IMAGE_BMC_UT3_0_B",
        "IMAGE_HMC_UT3_0_B",
        "IMAGE_CPLD_UT3_0_B",
        "IMAGE_SBIOS_UT3_0_B",
        "IMAGE_BMC_UT3_0_REV2_1",
        "IMAGE_HMC_UT3_0_REV2_1",
        "IMAGE_CPLD_UT3_0_REV2_1",
        "IMAGE_SBIOS_UT3_0_REV2_1",
        "BMC_IP",
        "DUT_IP",
        "HMC_IP",
        "NAUTILUS_VERSION",
        "HOST_MAC_ADDR",
        "HOST_IP_ADDR",
        "HOST_NAME",
        "IMAGE_BMC",
        "IMAGE_HMC",
        "IMAGE_CPLD",
        "VERSION_BMC",
        "VERSION_HMC",
        "VERSION_HMC_CPLD",
        "NVL0_ID",
        "NVL1_ID",
        "NVL_TYPE",
        "NVL0_SN",
        "NVL1_SN",
        "E4074_MAC",
        "",
        "",
        "110-0902-000",
        "110-0902-000_CPU_USE_TIMES",
        "110-0902-000_IN_STATION_TIME",
        "110-0902-000_CPU_LAST_RESET_TIME"

    ]
    
    try:
        # Open the CSV file for writing
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Define and write the header row for the CSV file
            header = ['Filepath'] + keys_to_find
            writer.writerow(header)
            
            # Process each log file found
            for file_path in log_files:
                print(f"\nProcessing '{file_path}'...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a list to hold the data for the current file's row
                # Use the full file_path to provide context in the CSV
                row_data = [file_path]
                
                # Find the value for each key and add it to the row data
                for key in keys_to_find:
                    result = get_value_from_log(content, key)
                    row_data.append(result)
                    print(f"- {key}: {result}")
                
                # Write the completed row to the CSV file
                writer.writerow(row_data)
                
        print(f"\nResults for all files have been successfully written to '{csv_output_path}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()