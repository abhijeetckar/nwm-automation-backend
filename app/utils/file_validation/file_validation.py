import pandas as pd
import zipfile
import gzip
import re

from app.models.file_models import DatColumn

# Specify the folder path
# folder_path = "downloads/C_VAR1_05032025_6.DAT"


def read_dat_file(file_path):
    """Reads a DAT file and extracts both Control and Detail records."""
    file_name = file_path.split('\\')[-1].split(".")[0]
    # Extract "C_VAR1"
    extracted_part = "_".join(file_name.split("_")[:-2])

    try:
        df = pd.read_csv(file_path, header=None,skiprows=1)

        detail_records = df[df[0] == 20]  # Extract detail records
        detail_records.columns = getattr(DatColumn, extracted_part)

        pd_table = pd.concat([detail_records], ignore_index=True)
        return pd_table
    except Exception as e:
        print(f"Error reading DAT file {file_path}: {e}")
        return None

def read_dat_integer_extention(file_path):
    """Reads a DAT file and extracts both Control and Detail records dynamically based on the identifier."""

    # Try reading the file with a flexible encoding
    try:
        df = pd.read_csv(file_path, header=None, delimiter="~", dtype=str, encoding="ISO-8859-1")
        df.fillna("", inplace=True)  # Replace NaN with empty strings

        unique_types = df[0].unique()  # Find all unique record types

        result_dfs = []
        extracted_part = file_path.split('\\')[-1].split(".")[0][2:-1]
        column_mappings = getattr(DatColumn, extracted_part)

        for record_type in unique_types:
            record_str = str(record_type).zfill(2)  # Format as "01", "02", etc.

            if record_str in column_mappings:
                subset_df = df[df[0] == record_type]  # Extract only the relevant rows
                expected_columns = column_mappings[record_str]


                actual_columns = subset_df.shape[1]
                expected_columns_count = len(expected_columns)

                if actual_columns > expected_columns_count:
                    print(f"More columns than expected in record {record_str}. Trimming extra columns.")
                    subset_df = subset_df.iloc[:, :expected_columns_count]  # Trim extra columns

                elif actual_columns < expected_columns_count:
                    print(f"Fewer columns than expected in record {record_str}. Padding missing columns.")
                    for i in range(actual_columns, expected_columns_count):
                        subset_df[i] = ""  # Add empty values for missing columns

                subset_df.columns = expected_columns  # Assign correct headers
                result_dfs.append(subset_df)

        if result_dfs:
            final_df = pd.concat(result_dfs, ignore_index=True)
            return final_df

        return None

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
        if file_extension.isdigit():
            return read_dat_integer_extention(file_path)
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
    k = extract_data("C:\\Users\\Lenovo\\Desktop\\workspace\\nwm-automation-backend_1\\downloads\\40DP37U.835385")
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
