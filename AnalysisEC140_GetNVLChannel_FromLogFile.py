import os
import csv
import re
import csv
import glob
import os
import sys
from pathlib import Path
from datetime import datetime, date

LBPCB_FAIL_SN = {'1821925953098':0, '1822025953976':0, 
                    '1822325950716':0, '1822325950442':0, 
                    '1822625959024':0, '1822625959209':0, 
                    '1822625957788':0, '1822325958301':0, 
                    '1822625957789':0, '1822625958383':0}

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
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            results = {}
            device_name = ""

            for i, line in enumerate(lines):
                procmod_0 = None
                
                if "FRU Device Description" in line:
                    if "ProcMod_0" in line:
                        procmod_0 = "ProcMod_0"

                if procmod_0 and (i + 2) < len(lines):
                    serial_line = lines[i + 2]
                    if "Board Serial Number" in serial_line:
                        serial_number = serial_line.split()[-1]
                        results["SN"] = serial_number
            sn_548 = results.get("SN", "N/A")

            for i, line in enumerate(lines):
                if "FRU Device Description" in line:
                    if "CBC_0" in line:
                        device_name = "CBC_0"
                    elif "CBC_1" in line:
                        device_name = "CBC_1"
                
                if device_name and (i + 2) < len(lines):
                    serial_line = lines[i + 2]
                    if "Board Serial Number" in serial_line:
                        serial_number = serial_line.split()[-1]
                        results[device_name] = serial_number

            cbc0 = results.get("CBC_0")
            cbc1 = results.get("CBC_1")

            if cbc0 in LBPCB_FAIL_SN: 
                LBPCB_FAIL_SN[cbc0] += 1
                print(f"Key '{cbc0}' found and its value was incremented.")
            else:
                 print(f"Key '{cbc0}' not found in the dictionary.")

            if cbc1 in LBPCB_FAIL_SN: 
                LBPCB_FAIL_SN[cbc1] += 1
                print(f"Key '{cbc1}' found and its value was incremented.")
            else:
                 print(f"Key '{cbc1}' not found in the dictionary.")

            # Iterate through each line with its index
            for i, line in enumerate(lines):
                # Condition 1: Check for header keywords in the current line
                if "Exit Code" in line and "Component Id" in line:
                    # Ensure we don't go out of bounds when checking the next line
                    if i + 2 < len(lines):
                        next_line = lines[i+2]

                        # Condition 2: Check for the specific module code in the next line
                        if "MODS-000000000140" in next_line:
                            # Use regular expressions to find the data in the next line.
                            # This pattern is more specific to match formats like "GPU0_..."
                            gpu_match = re.search(r"(GPU\d+_\S+),", next_line)
                            # This pattern looks for "Nvlink" followed by space(s) and digits.
                            nvlink_match = re.search(r"Nvlink\s+(\d+)", next_line)
                            # This pattern looks for "Lane" followed by space(s) and digits.
                            lane_match = re.search(r"Lane\s+(\d+)", next_line)

                            # Extract the matched group, otherwise assign "N/A"
                            gpu = gpu_match.group(1) if gpu_match else "N/A"
                            nvlink = nvlink_match.group(1) if nvlink_match else "N/A"
                            lane = lane_match.group(1) if lane_match else "N/A"

                            # Store the found data
                            extracted_data.append({
                                'SN': sn_548,
                                'log_file_name': os.path.basename(file_path),
                                'GPU': gpu,
                                'Nvlink': nvlink,
                                'Lane': lane,
                                'NVL0_SN' : cbc0,
                                'NVL1_SN' : cbc1
                            })
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
    if "_NVL_" in filename:
        return True
    
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
    LOG_PATTERN = 'Z:/Bianca/????-??-??/??/*.log'
    
    # 2. Set your desired date range
    START_DATE = "2025-11-01"
    END_DATE = "2025-11-06"

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

    csv_output_path = 'core_error_140_nvlchannel.csv'
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
            fieldnames = ['SN', 'log_file_name', 'GPU', 'Nvlink', 'Lane', 'NVL0_SN', 'NVL1_SN']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_data)

        print(f"\nSuccessfully parsed log files. Data written to {csv_output_path}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

    print(LBPCB_FAIL_SN)

if __name__ == "__main__":
    main()
