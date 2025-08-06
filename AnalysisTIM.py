# For log analysis(TIM), 2025-08-06.
# kevin.hw.huang@fii-foxconn.com 

import csv
import glob
import os

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
    log_files = glob.glob('????-??-??/??/*.txt')
    csv_output_path = 'tim_usage_analysis.csv'
    
    if not log_files:
        print("No .txt log files found in any 'yyyy-mm-dd' subdirectories.")
        return

    print(f"Found {len(log_files)} log file(s) to process.")

    keys_to_find = [
        "TIME_START_CLIENT",
        "110-0902-000",
        "110-0902-000_CPU_USE_TIMES",
        "110-0902-000_IN_STATION_TIME",
        "110-0902-000_CPU_LAST_RESET_TIME",
        "PROCESS",
        "DIAG",
        "TESTER_TYPE",
        "FIXTURE",
        "PRODUCT",
        "SN",
        "PN",
        "TestTime",
        "TestStatus",
        "TestErrorCode",
        "TestErrorMessage",
        "CoreErrorCode",
        "CoreErrorMessage"
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