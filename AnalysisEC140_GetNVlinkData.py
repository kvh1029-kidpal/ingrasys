import os
import csv
import re

LBPCB_FAIL_SN = {'1821925953098':0, '1822025953976':0, 
                    '1822325950716':0, '1822325950442':0, 
                    '1822625959024':0, '1822625959209':0, 
                    '1822625957788':0, '1822325958301':0, 
                    '1822625957789':0, '1822625958383':0}

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

def main():
    """
    Main function to find log files in a specific directory,
    parse them, and write the results to a CSV file.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # log_folder_name = "EC140Logs"
    # log_folder_path = os.path.join(script_dir, log_folder_name)
    log_folder_path = "Z:/ForHsunwen" 
    output_csv_path = os.path.join(script_dir, 'core_error_140_NVLChannel.csv')
    all_data = []

    # Check if the log directory exists
    if not os.path.isdir(log_folder_path):
        print(f"Error: The directory '{log_folder_path}' was not found in the script's location.")
        print(f"Please make sure your log files are in: {log_folder_path}")
        return

    print(f"Searching for .log files in: {log_folder_path}")

    # Find all files ending with .log in the specified directory
    for filename in os.listdir(log_folder_path):
        if filename.endswith(".log"):
            file_path = os.path.join(log_folder_path, filename)
            print(f"Parsing {filename}...")
            data = parse_log_file(file_path)
            if data:
                all_data.extend(data)

    if not all_data:
        print("No matching log entries found in any of the log files.")
        return

    # Write the extracted data to a CSV file
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define the column headers for the CSV
            fieldnames = ['SN', 'log_file_name', 'GPU', 'Nvlink', 'Lane', 'NVL0_SN', 'NVL1_SN']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_data)

        print(f"\nSuccessfully parsed log files. Data written to {output_csv_path}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

    print(LBPCB_FAIL_SN)

if __name__ == "__main__":
    main()
