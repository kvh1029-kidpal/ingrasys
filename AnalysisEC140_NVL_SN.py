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

def format_iso_datetime(iso_string: str) -> str | None:
    """
    Parses an ISO 8601 formatted datetime string and returns it
    in 'YYYY-MM-DD HH:MM:SS' format.

    Args:
        iso_string: The input datetime string in ISO format.

    Returns:
        A string formatted as 'YYYY-MM-DD HH:MM:SS', or None
        if the input string is invalid.
    """
    try:
        # 1. Parse the ISO string into a datetime object
        dt_object = datetime.fromisoformat(iso_string)
        
        # 2. Format the datetime object into the desired string format
        #    %Y = YYYY (4-digit year)
        #    %m = mm (2-digit month)
        #    %d = dd (2-digit day)
        #    %H = HH (2-digit hour, 24-hour clock)
        #    %M = MM (2-digit minute)
        #    %S = SS (2-digit second)
        formatted_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        
        # 3. Return the result
        return formatted_string
        
    except ValueError:
        # Handle cases where the input string is not a valid ISO format
        print(f"Error: Invalid datetime string provided: '{iso_string}'")
        return None
    except TypeError:
        # Handle cases where input is not a string
        print(f"Error: Input must be a string, but got {type(iso_string)}")
        return None

def get_value_from_log(file_content: str, key: str) -> str:
    """
    Parses the given text to find the value for a specific key using an exact match.

    Args:
        file_content: A string containing the log file's text.
        key: The exact key to search for.

    Returns:
        The corresponding value as a string, or "Value not found" message.
    """
    for line in file_content.splitlines():
        parts = line.split('=', 1)
        if len(parts) == 2:
            found_key = parts[0].strip()
            if found_key == key:
                value = parts[1].strip()
                return value
    return "Value not found"

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
    LOG_PATTERN = 'Z:/MACHINE/Analysis/????-??-??/??/*.txt'
    
    # 2. Set your desired date range
    START_DATE = "2025-10-22" # "2025-10-01"
    END_DATE = "2025-11-03" #"2025-10-30"

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
        print("--- No .txt files found matching the criteria. ---")
        return
    
    csv_output_path = 'core_error_140_analysis.csv'
    
    # The primary key to filter by
    filter_errorcode = "CoreErrorCode"
    filter_process = "PROCESS"
    
    # The other keys to extract if the filter matches
    keys_to_extract = [
        "SN",
        "PN",
        "SKU",
        "PROCESS",
        "CoreErrorCode",
        "NVL0_ID",
        "NVL0_SN",
        "NVL1_ID",
        "NVL1_SN",
        "DIAG",
        "BMC_IP",
        "DUT_IP",
        "HOST_IP_ADDR",
        "FIXTURE",
        "HOST_DATE_TIME",
        "TIME_BEGIN_RECIPE",
        "TIME_END_RECIPE"
    ]
    
    # List to hold all the rows of data for the CSV file
    all_results = []

    try:
        # Process each log file found
        for file_path in final_file_list:
            if not check_filename(file_path):
                print(f"\nNot FCT or NVL log file: '{file_path}'")
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get the value of the key we are filtering by
            error_code = get_value_from_log(content, filter_errorcode)
            process = get_value_from_log(content, filter_process)

            # Check if the error code ends with "140"
            if error_code.endswith("140") and ( process.endswith("FCT") or process.endswith("NVL") ):
                print(f"\nFound matching file: '{file_path}' (CoreErrorCode: {error_code})")
                
                # Create a dictionary to hold the data for the current file
                result_row = {'Filepath': file_path, filter_errorcode: error_code}
                
                # If it matches, extract the other specified values
                for key in keys_to_extract:
                    value = get_value_from_log(content, key)
                    if key == "TIME_BEGIN_RECIPE" or key == "TIME_END_RECIPE":
                        value = format_iso_datetime(value)

                    result_row[key] = value
                    print(f"- {key}: {value}")
                
                all_results.append(result_row)
            else:
                # Optional: print which files are being skipped
                print(f". Skipping '{os.path.basename(file_path)}'")

        # After checking all files, write the collected results to CSV
        if not all_results:
            print("\nNo log files matched the criteria (CoreErrorCode ending in '140').")
            return
            
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define the header based on the keys of the first result
            header = ['Filepath', filter_errorcode] + keys_to_extract
            writer = csv.DictWriter(csvfile, fieldnames=header)
            
            # Write the header and all the result rows
            writer.writeheader()
            writer.writerows(all_results)
            
        print(f"\nAnalysis complete. Results for {len(all_results)} matching file(s) written to '{csv_output_path}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Standard entry point for a Python script
if __name__ == "__main__":
    main()
