import pandas as pd
import zipfile
import gzip
import re

# Specify the folder path
folder_path = "downloads"


def read_dat_file(file_path):
    """Reads a DAT file and extracts both Control and Detail records."""
    col_names_detail = [
        "Record Type", "Sec Symbol", "Sec Series", "ISIN", "Security VAR", "Filler",
        "VAR Margin", "Extreme Loss Rate", "Additional Margin", "Daily Margin Rate"
    ]

    try:
        df = pd.read_csv(file_path, header=None,skiprows=1)

        detail_records = df[df[0] == 20]  # Extract detail records
        detail_records.columns = col_names_detail

        pd_table = pd.concat([detail_records], ignore_index=True)
        return pd_table
    except Exception as e:
        print(f"Error reading DAT file {file_path}: {e}")
        return None
def extract_fixed_column_tables(lines):
    """Extract tables from a CSV.GZ file with fixed column structures."""
    try:
        all_data = []
        column_headers = None

        # Section header pattern
        section_pattern = re.compile(r'^(SEC|GMF|GSEC|CMF|CB|OMF|NMF)\s*$', re.IGNORECASE)

        for line in lines:
            # Detect section headers (ignored since we don't need "Table Name" column)
            if section_pattern.match(line):
                continue

                # Detect headers dynamically
            elif column_headers is None and re.search(r'(TM code|Client/CP code|INSTRUMENT TYPE)', line, re.IGNORECASE):
                column_headers = re.split(r'[\t,]+', line.strip())

            # Add data rows (ensuring correct column count)
            elif column_headers and line:
                row = re.split(r'[\t,]+', line.strip())

                # **Skip row if it exactly matches column headers**
                if row != column_headers:
                    all_data.append(row)

        # Create DataFrame
        if all_data and column_headers:
            df = pd.DataFrame(all_data, columns=column_headers)
            return [df]

        return []
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []



def read_file(file_path):
    """ Use swtich case instead of if elif"""
    try:
        file_extension = file_path.split('.')[-1].lower()  # Convert to lowercase for consistency
        match file_extension:
            case "csv":
                return pd.read_csv(file_path, on_bad_lines='skip', engine='python')
            case "zip":
                with zipfile.ZipFile(file_path, 'r') as z:
                    with z.open(z.namelist()[0]) as f:
                        return pd.read_csv(f, on_bad_lines='skip', engine='python')
            case "gz":
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    all_dataframes = extract_fixed_column_tables(lines)
                    return pd.concat(all_dataframes, ignore_index=True)
            case "dat":
                return read_dat_file(file_path)
            case _:
                print(f"Skipping unsupported file: {file_path}")
                return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def extract_data(file_path):
    df = read_file(file_path)
    return df


try:
    k = extract_data("C:\\Users\\Lenovo\\Desktop\\workspace\\nwm-automation-backend_1\\downloads\\C_VAR1_05032025_6.DAT")
    print(k)
except Exception as exp:
    print(exp)


# """ Extract the Multiple Tables From the CSV"""
# def extract_fixed_column_tables(file_path):
#     """Extract multiple tables from a CSV file with fixed column structures."""
#     try:
#         with gzip.open(file_path, 'rt') as f:
#             lines = f.readlines()
#
#         tables = {}
#         current_table_name = None
#         current_data = []
#         column_headers = None
#
#         for i, line in enumerate(lines):
#             line = line.strip()
#
#             # Detect table names like "SEC", "NMF", etc.
#             if re.match(r'^\s*(SEC|NMF|OMF|CB|CASH COMPONENT|NON CASH COMPONENT)\s*$', line):
#                 if current_table_name and current_data:
#                     # Save previous table
#                     df = pd.DataFrame(current_data, columns=column_headers)
#                     tables[current_table_name] = df
#
#                 # Start a new table
#                 current_table_name = line.strip()
#                 current_data = []
#                 column_headers = None  # Reset column headers for the new table
#
#             elif current_table_name and column_headers is None and "TM code" in line:
#                 # Detect column headers
#                 column_headers = line.split("\t")
#
#             elif column_headers and line:
#                 # Extract table data rows
#                 row = line.split("\t")
#                 if len(row) == len(column_headers):  # Ensure correct column count
#                     current_data.append(row)
#
#         # Save last table
#         if current_table_name and current_data:
#             df = pd.DataFrame(current_data, columns=column_headers)
#             tables[current_table_name] = df
#
#         return tables
#
#     except Exception as e:
#         print(f"Error extracting tables: {e}")
#         return {}
#
# # Example Usage
# file_path = "multiple/C_90296_SEC_PLEDGE_06032025_01.csv.gz"
# tables = extract_fixed_column_tables(file_path)
#
# # Display extracted tables
# for name, df in tables.items():
#     print(f"\nTable: {name}")
#     print(df.head())
#     print("-" * 50)
#
# # Save tables to CSV or JSON
# for name, df in tables.items():
#     df.to_csv(f"{name}.csv", index=False)
#     df.to_json(f"{name}.json", orient="records", indent=4)
