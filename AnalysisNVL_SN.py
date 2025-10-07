import os

LBPCB_FAIL_SN = {'1821925953098':0, '1822025953976':0, 
                    '1822325950716':0, '1822325950442':0, 
                    '1822625959024':0, '1822625959209':0, 
                    '1822625957788':0, '1822325958301':0, 
                    '1822625957789':0, '1822625958383':0}

def find_serial_numbers(root_directory):
    """
    Searches for *.txt files in a directory and its subdirectories,
    and extracts NVL0_SN and NVL1_SN values.

    Args:
        root_directory (str): The starting path to search from.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              the data found in one file.
    """
    # A list to store the results from all files
    results = []

    # os.walk() efficiently goes through the entire directory tree
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # Process only if the file has a .txt extension
            if 'NVL' in filename and filename.endswith('.txt'):
                filepath = os.path.join(dirpath, filename)
                
                # Use variables to store the values found in the current file
                nvl0_sn = None
                nvl1_sn = None

                try:
                    print(f"Processing file: {filepath}")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Clean up the line by removing leading/trailing whitespace
                            clean_line = line.strip()

                            # Check for the keys and extract their values
                            if clean_line.startswith('NVL0_SN'):
                                # Split the line at '=' and get the second part (the value)
                                nvl0_sn = clean_line.split('=')[1].strip()
                            
                            elif clean_line.startswith('NVL1_SN'):
                                # Split the line at '=' and get the second part (the value)
                                nvl1_sn = clean_line.split('=')[1].strip()

                    # Only add the file to our results if we found at least one key
                    if nvl0_sn is not None or nvl1_sn is not None:
                        if (nvl0_sn in LBPCB_FAIL_SN):
                                LBPCB_FAIL_SN[nvl0_sn] +=1
                        if (nvl1_sn in LBPCB_FAIL_SN):
                                LBPCB_FAIL_SN[nvl0_sn] +=1

                        # results.append({
                        #     'filepath': filepath,
                        #     'NVL0_SN': nvl0_sn,
                        #     'NVL1_SN': nvl1_sn
                        # })

                except Exception as e:
                    print(f"⚠️ Could not read or process file '{filepath}': {e}")
    
    return results

# --- How to Use ---

# 1. Set the main folder you want to search in
search_path = 'Z:/MACHINE/Analysis'

# 2. Run the function
extracted_data = find_serial_numbers(search_path)

# # 3. Print the results
# if not extracted_data:
#     print(f"No '.txt' files with NVL0_SN or NVL1_SN found under '{search_path}'.")
# else:
#     print("✅ Successfully extracted data from the following files:")
#     print("=" * 50)
#     for item in extracted_data:
#         print(f"File: {item['filepath']}")
#         print(f"  NVL0_SN: {item['NVL0_SN']}")
#         print(f"  NVL1_SN: {item['NVL1_SN']}")
#         print("-" * 20)

print(LBPCB_FAIL_SN)