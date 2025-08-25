import csv
import glob
import os

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

def main():
    """
    Main function to run the script. It finds all .txt log files within any
    'yyyy-mm-dd' formatted subdirectories, filters them based on a CoreErrorCode,
    extracts relevant data, and writes the results to a CSV file.
    """
    # Use glob to find all .txt files in directories matching the 'yyyy-mm-dd' pattern
    log_files = glob.glob('????-??-??/??/*.txt')
    csv_output_path = 'core_error_140_analysis.csv'
    
    if not log_files:
        print("No .txt log files found in any 'yyyy-mm-dd' subdirectories.")
        return

    print(f"Found {len(log_files)} log file(s) to scan.")

    # The primary key to filter by
    filter_key = "CoreErrorCode"
    
    # The other keys to extract if the filter matches
    keys_to_extract = [
        "SN",
        "110-0902-000_CPU_USE_TIMES",
        "110-0902-000_CPU_LAST_RESET_TIME",
        "110-0902-000_IN_STATION_TIME"
    ]
    
    # List to hold all the rows of data for the CSV file
    all_results = []

    try:
        # Process each log file found
        for file_path in log_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get the value of the key we are filtering by
            error_code = get_value_from_log(content, filter_key)

            # Check if the error code ends with "140"
            if error_code.endswith("140"):
                print(f"\nFound matching file: '{file_path}' (CoreErrorCode: {error_code})")
                
                # Create a dictionary to hold the data for the current file
                result_row = {'Filepath': file_path, filter_key: error_code}
                
                # If it matches, extract the other specified values
                for key in keys_to_extract:
                    value = get_value_from_log(content, key)
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
            header = ['Filepath', filter_key] + keys_to_extract
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
