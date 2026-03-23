import os
import csv
import re
import csv
import glob
import os
import sys
from pathlib import Path
from datetime import datetime, date

# LBPCB_FAIL_SN = {'1821925953098':0, '1822025953976':0, 
#                     '1822325950716':0, '1822325950442':0, 
#                     '1822625959024':0, '1822625959209':0, 
#                     '1822625957788':0, '1822325958301':0, 
#                     '1822625957789':0, '1822625958383':0}
LBPCB_FAIL_SN = {}

# TO-DO: Initialize a dictionary to keep track of total LBPCB serial numbers
# TOTAL_LBPCB_SN = {}

def extract_tray_sn(line: str, search_key: str) -> str | None:
    """
    Extracts the value following 'TRAY_SN:' from a given string.
    
    Args:
        line: The input string containing the key-value pair.
        
    Returns:
        The extracted serial number as a string, or None if the key isn't found.
    """
    #key = "TRAY_SN:"
    key = search_key
    
    # Check if the key exists in the line
    if key in line:
        # Split the string by the key and take the second part
        # The 1 ensures we only split on the first occurrence
        parts = line.split(key, 1)
        if len(parts) > 1:
            # strip() removes any leading/trailing whitespace or newlines
            return parts[1].strip()
            
    return None

def process_file_for_tray_sn(file_path: str, search_key: str):
    """
    Reads a file line by line and attempts to find the TRAY_SN key.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                result = extract_tray_sn(line, search_key)
                if result:
                    return result
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    
    return None



# def extract_keyword(line: str, key: str = "TRAY_SN") -> str | None:
#     """
#     Extracts the value following a specific key (e.g., 'TRAY_SN:') from a given string.
#     """
#     search_key = f"{key}:"
#     if search_key in line:
#         parts = line.split(search_key)
#         if len(parts) > 1:
#             return parts[1].strip()
#     return None

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

def parse_log_file(file_path):
    """
    Parses a single log file to find and extract specific data from lines
    that follow a specific header line.

    Args:
        file_path (str): The full path to the log file.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              the extracted data for a matching log entry. Returns an
              empty list if no matching entries are found.
    """
    extracted_data = []

    board_sn = process_file_for_tray_sn(file_path, "BrdSN:")
    if board_sn:
        print(f"Extracted BrdSN: {board_sn}")
    else:
        print("BrdSN key not found in the file.")

    tray_sn = process_file_for_tray_sn(file_path, "TRAY_SN:")
    if tray_sn:
        print(f"Extracted TRAY_SN: {tray_sn}")
    else:
        print("TRAY_SN key not found in the file.")
    
    flat_id = process_file_for_tray_sn(file_path, "FLAT ID:")
    if flat_id:
        print(f"Extracted FLAT ID: {flat_id}")
    else:
        print("FLAT ID key not found in the file.")
    
    fox_routing = process_file_for_tray_sn(file_path, "FOX_Routing:")
    if fox_routing:
        print(f"Extracted FOX Routing: {fox_routing}")
    else:
        print("FOX_Routing key not found in the file.")

    error_code = process_file_for_tray_sn(file_path, "Error Code:")
    if error_code:
        print(f"Extracted Error Code: {error_code}")
    else:
        print("Error Code key not found in the file.")

    product_pn = process_file_for_tray_sn(file_path, "PN:")
    if product_pn:
        print(f"Extracted PN: {product_pn}")
    else:
        print("PN key not found in the file.")

    diag_version = process_file_for_tray_sn(file_path, "DiagVer:")
    if diag_version:
        print(f"Extracted DiagVer: {diag_version}")
    else:
        print("DiagVer key not found in the file.")
    
    start_test_time = process_file_for_tray_sn(file_path, "StartTestTime:")
    if start_test_time:
        print(f"Extracted StartTestTime: {start_test_time}")
    else:
        print("StartTestTime key not found in the file.")

    end_test_time = process_file_for_tray_sn(file_path, "EndTestTime:")
    if end_test_time:
        print(f"Extracted EndTestTime: {end_test_time}")
    else:
        print("EndTestTime key not found in the file.")

    # sn_548 = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # results_sn = {}
            results_cbc = {}
            device_name = ""

            for i, line in enumerate(lines):
                procmod_0 = None
                
                if "FRU Device Description" in line:
                    if "ProcMod_0" in line:
                        procmod_0 = "ProcMod_0"
                    if "CBC_0" in line:
                        device_name = "CBC_0"
                    elif "CBC_1" in line:
                        device_name = "CBC_1"

                if device_name and (i + 2) < len(lines):
                    serial_line = lines[i + 2]
                    if "Board Serial Number" in serial_line:
                        serial_number = serial_line.split()[-1]
                        results_cbc[device_name] = serial_number

                # if procmod_0 and (i + 2) < len(lines):
                #     serial_line = lines[i + 2]
                #     if "Board Serial Number" in serial_line:
                #         serial_number = serial_line.split()[-1]
                #         results_sn["SN"] = serial_number
                #         sn_548 = results_sn.get("SN", "N/A")

            
            cbc0 = results_cbc.get("CBC_0")
            cbc1 = results_cbc.get("CBC_1")

            # if cbc0 in LBPCB_FAIL_SN: 
            #     LBPCB_FAIL_SN[cbc0] += 1
            #     print(f"Key '{cbc0}' found and its value was incremented.")
            # else:
            #      print(f"Key '{cbc0}' not found in the dictionary.")

            # if cbc1 in LBPCB_FAIL_SN: 
            #     LBPCB_FAIL_SN[cbc1] += 1
            #     print(f"Key '{cbc1}' found and its value was incremented.")
            # else:
            #      print(f"Key '{cbc1}' not found in the dictionary.")

        # if error_code == 'E108003006_023-049-0-000000000008':
        if error_code == 'E028163006_000-001-1-0-008-00-546-284':
            # Store the found data
            extracted_data.append({
                'SN': board_sn,
                'Tray_SN': tray_sn,
                'POD_Rack_Slot': flat_id,
                'FOX_Routing': fox_routing,
                'Error_Code': error_code,
                'GPU': None,
                'Nvlink': None,
                'Lane': None,
                'NVL0_SN' : cbc0,
                'NVL1_SN' : cbc1,
                'PN' : product_pn,
                'Diag' : diag_version,
                'StartTestTime': start_test_time,
                'EndTestTime': end_test_time,
                'log_file_name': os.path.basename(file_path)
            })
            print(extracted_data)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    return extracted_data

def check_filename(filename: str) -> bool:
    """
    Checks if a filename contains either '_FCT_' or '_NVL_'.

    Args:
        filename: The name of the file (e.g., "my_file.txt").

    Returns:
        True if either substring is found, False otherwise.
    """
    if "_FCT_" in filename:
        return True
    # if "_NVL_" in filename:
    #     return True
    # if "_IST_" in filename:
    #    return True
    
    # If neither substring was found, return False
    return False

def main():
    """
    Main function to run the script. It finds all .txt log files within any
    'yyyy-mm-dd' formatted subdirectories, filters them based on a CoreErrorCode,
    extracts relevant data, and writes the results to a CSV file.
    """
    # --- !!! IMPORTANT: SET YOUR VARIABLES HERE !!! ---
    
    # 1. This is your original glob pattern
    #    Note: Use forward slashes '/'.
    # LOG_PATTERN = 'Z:/Bianca/GDL_20260214_0317_Log/Mar_logs_archive/????-??-??/??/*.log'
    # LOG_PATTERN = 'Z:/Bianca/????-??-??/??/*.log'
    LOG_PATTERN = 'D:/TestLogs/????-??-??/??/*.log'
    # LOG_PATTERN = 'C:/Users/kvh10/Downloads/OneDrive_1_2026-3-17/2026-03-16_23_FCT_logs/????-??-??/??/*.log'
    
    # 2. Set your desired date range
    START_DATE = "2026-03-21" # "2026-01-21" # "2025-10-10"
    END_DATE   = "2026-03-21" # "2026-02-01" # "2025-10-15"

    # --- Run the function ---
    
    # Note: This will only find files if they *actually exist*
    # on your 'Z:/' drive when you run the script.
    
    final_file_list = get_log_files_in_date_range(LOG_PATTERN, START_DATE, END_DATE)
    # --- Print the results ---
    if final_file_list:
        # print(f"--- Found {len(final_file_list)} matching .txt files in range ---")
        # for file_path in final_file_list:
        #     print(file_path)
        pass
    else:
        print("--- No .log files found matching the criteria. ---")
        return

    csv_output_path = 'EC008_' + START_DATE + '_' + END_DATE + '_EC284.csv'
    all_data = []

    # Find all files ending with .log in the specified directory
    for file_path in final_file_list:
        if not check_filename(file_path):
            print(f"\nNot FCT or NVL log file: '{file_path}'")
            continue

        if file_path.endswith(".log"):
            print(f"Parsing {file_path}...")
            data = parse_log_file(file_path)
            if data:
                all_data.extend(data)

    if not all_data:
        print("No matching log entries found in any of the log files.")
        return

    # Write the extracted data to a CSV file
    try:
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define the column headers for the CSV
            fieldnames = ['SN', 'Tray_SN', 'POD_Rack_Slot', 'FOX_Routing', 'Error_Code', 'GPU', 'Nvlink', 'Lane', 'NVL0_SN', 'NVL1_SN', 'PN', 'Diag', 'StartTestTime', 'EndTestTime', 'log_file_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_data)

        print(f"\nSuccessfully parsed log files. Data written to {csv_output_path}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

    print(LBPCB_FAIL_SN)

if __name__ == "__main__":
    main()
