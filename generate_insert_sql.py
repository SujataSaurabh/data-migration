import csv, sys
import re
import os
from datetime import datetime
import codecs
from generate_create_table_sql import update_fields
# 
# Increase the CSV field size limit
csv.field_size_limit(sys.maxsize)

def read_csv_file(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file path.")
        return
    result = []
    print
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                result.append(row)
    except csv.Error as e:
        print(f"CSV Error: {e}")
        print(f"Field larger than limit found in file: {file_path}")
        row = 0 
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                row+=1
                print(f"Row: {row}")
                print(f"Line length: {len(line)} and   csv.field_size_limit(sys.maxsize): {csv.field_size_limit(sys.maxsize)}")
                if len(line) > csv.field_size_limit(sys.maxsize):
                    print(f"Line length: {len(line)} at row {row} and {sys.maxsize}")
                    print(f"Problematic field: {line.strip()}")
        raise
    return result 
# 
def extract_column_info(schema_sql):
    with open(schema_sql, 'r', encoding='utf-8') as file:
        sql_query = file.read()

    # get table name
    table_name = re.search(r'CREATE TABLE IF NOT EXISTS (\w+)', sql_query)
    table_name = table_name.group(1)
    print("table_name == ", table_name)
    if not table_name:
        print("Invalid SQL query format")
        return

    # Extract column definitions (between parentheses)
    match = re.search(r'\((.*)\)', sql_query, re.DOTALL)
    if not match:
        return []
    
    columns_data = match.group(1).split(',\n')

    ind = 0 
    result = []
    for col in columns_data:
        col = col.strip()
        if col.lower().startswith("primary key"):
            continue  # Skip primary key constraint
        parts = col.split()
        col_name = parts[0]
        col_type = parts[1]
        if "precision" in parts[1]:
            col_type += " " + parts[2]
        
        result.append((ind, (col_name, col_type)))
        ind += 1
    return result, table_name
     
# def extract_column_info(schema_sql):
#     with open(schema_sql, 'r') as f:
#         schema_sql = f.read()
#         # extract table name 
#     table_name = re.search(r'CREATE TABLE IF NOT EXISTS (\w+)', schema_sql)
#     if not table_name:
#         print("Invalid SQL query format")
#         return
#     table_name = table_name.group(1)
# #    print("table_name == ", table_name)
#      # Extract only the part after '('
#     match = re.search(r'\(\s*(.*?)\s*\)', schema_sql, re.DOTALL)
#     if not match:
#         return {}
#     columns_part = match.group(1)
    
#     # Extract column definitions (ignoring PRIMARY KEY and constraints)
#     columns = re.findall(r'\s*(\w+)\s+([a-zA-Z]+)(?:\s+NOT NULL)?', columns_part)
    
#     # Filter out the PRIMARY KEY and constraints
#     columns = [col for col in columns if col[0].upper() != "PRIMARY"]
    
#     # Assign column numbers and format output
#     column_info = {idx: (col[0], col[1]) for idx, col in enumerate(columns)}
#     return column_info, table_name

def identify_column_types(table_schema):
    columns, table_name = extract_column_info(table_schema)
#    print("columns == ", columns)
    #  identify column types
    col_id_date = [item[0] for item in columns if item[1][1] == 'date']
    col_id_time = [item[0] for item in columns if item[1][1] == 'time']
    col_id_boolean = [item[0] for item in columns if item[1][1] == 'boolean']
    col_id_varchar = [item[0] for item in columns if item[1][1] == 'varchar']
    col_id_bytea = [item[0] for item in columns if item[1][1] == 'bytea']
    # print(f"Table: {table_name} has {col_id_date} date columns and {col_id_boolean} boolean columns.")
    print(f"Table: {table_name} has columns- {len(columns)}")
    return columns, col_id_date, col_id_boolean, col_id_varchar, col_id_time, col_id_bytea
#
def process_bytea(col_id, table_name, bytea_value):
    # This function is for BeamContact table to replace PRTLetter_ value with Empty String
    return " '' "

def process_dates(col_id, table_name,dates):
    # If dates are null then replaceing them with 2050-01-01 to be consistent with the date format.
    if dates == '0000/00/00 00:00:00:00' or dates=='0000-00-00':#            print("Error: Invalid date format '0000/00/00 00:00:00:00' found at index ", {dates.index('0000/00/00 00:00:00:00')})
        # return  " '0000-00-00' " 
        return  " '2050-01-01' " 
    if dates=='0000-00-00':
        return  " '2050-01-01' " 
    try:
        dt = datetime.strptime(dates, "%Y/%m/%d %H:%M:%S:%f")
        # Formatting it to PostgreSQL compatible format
        return  f"'{dt.strftime('%Y-%m-%d')}'"
    except ValueError as e: 
       print(f"Error converting date {dates} at col: {col_id}: {e} in table: {table_name}")
       return  " '0000-00-00' " 
    
def process_time(col_id, table_name, time_value):
    try:
        # Split the time value into components
        time_parts = time_value.split(':')
        
        # Handle cases with more than three components (e.g., HH:MM:SS:MS)
        if len(time_parts) > 3:
            # Combine the first three components and append milliseconds
            sanitized_time = ':'.join(time_parts[:3])
            milliseconds = time_parts[3] if len(time_parts[3]) <= 3 else time_parts[3][:3]  # Take up to 3 digits for milliseconds
            sanitized_time = f"{sanitized_time}.{milliseconds}"
        else:
            # If the time value is already in HH:MM:SS format
            sanitized_time = ':'.join(time_parts)

        # Parse the sanitized time value
        dt = datetime.strptime(sanitized_time, "%H:%M:%S.%f")
        # print(f"Processed time_value: {sanitized_time} in table: {table_name}")
        
        # Formatting it to PostgreSQL compatible format
        return f"'{dt.strftime('%H:%M:%S.%f')[:-3]}'"  # Truncate to milliseconds
    except ValueError as e:
        print(f"Error converting time {time_value} at col: {col_id}: {e} in table: {table_name}")
        return " '00:00:00.000' "
   
def process_string(col_id, table_name, text):
    try:
        # text = text.replace("'", "''")  # Escape single quotes
        # text = text.replace('"', '""')  # Escape double quotes
        return f"'{text}'"
    except Exception as e:  
        print(f"Error processing string {text} at col: {col_id}: {e} in table: {table_name}")
        return " '' "
    pass

def update_data_into_postgres_format(file_path, table_schema):
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file path.")
        return
    # read table schema , extract column names and data types
    data = read_csv_file(file_path) 
    schema, table_name = extract_column_info(table_schema)
    if not data or not schema:
        return
    # check if the schema has date and boolean values
    columns, col_id_date, col_id_boolean, col_id_varchar, col_id_time, col_id_bytea = identify_column_types(table_schema)
    if col_id_bytea:
        for row in data[1:]:
            for col_id in col_id_bytea:
                if col_id < len(row):
                    row[col_id] = process_bytea(col_id, table_name, row[col_id])
                else:
                    pass
                    # print(f"Error: Column index {col_id} is out of range: {len(row)} in table: {table_name}")
    
    # update date in postgres format and boolean values
    if col_id_varchar:
        for row in data[1:]:
            for col_id in col_id_varchar:
                if col_id < len(row):
                    row[col_id] = process_string(col_id, table_name, row[col_id])
                else:
                    pass
                    # print(f"Error: Column index {col_id} is out of range: {len(row)} in table: {table_name}")
    if col_id_date:
        for row in data[1:]:
            for col_id in col_id_date:
                if col_id < len(row):
                 row[col_id] = process_dates(col_id, table_name,row[col_id])
                else:
                    pass
                    # print(f"Error: Column index {col_id} is out of range: {len(row)} in table: {table_name}")
    if col_id_time:
        for row in data[1:]:
            for col_id in col_id_time:
                if col_id < len(row):
                 row[col_id] = process_time(col_id, table_name,row[col_id])
                else:
                    pass
    if col_id_boolean:  
        for row in data[1:]:
            for col_id in col_id_boolean:
                if col_id < len(row):
                # if len(row) < col_id:
                #     # print(f"Error: Column index {col_id} is out of range: {len(row)} in table: {table_name}")
                #     continue
                    row[col_id] = " 't' " if row[col_id] == '1' else " 'f' " 
                else:
                    pass
                    # print(f"Error: Column index {col_id} is out of range: {len(row)} in table: {table_name}")
    return table_name, data
# 
def  get_primary_key_field(schema_file):
    #  extract primary key field
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
        primary_key = re.search(r'PRIMARY KEY \((\w+)\)', schema_sql)
        if not primary_key:
            print("NO PRIMARY KEY FOUND")
            return
        return primary_key.group(1)
# 
def generate_insert_sql(file_path, schema_file, output_file):
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file path.")
        return
    primary_key_field = get_primary_key_field(schema_file)

    table_name, data = update_data_into_postgres_format(file_path, schema_file)
    if not data:
        return
    # start putting the data into insert values command for postgres query
    insert_values = []
    for row in data[1:]:
        insert_values.append(f"({','.join(row)})")
    insert_values = ',\n'.join(insert_values)
    columns = data[0]
    updated_columns = []
    # update column names with postgres naming conventions
    for column in columns:
        updated_columns.append(update_fields([column])[
                    0]) # Update field name with naming conventions  # field_name = update_fields([field_name])[

    # create insert query for postgres
    insert_query = f"INSERT INTO {table_name} ({','.join(updated_columns)}) VALUES\n{insert_values} ON CONFLICT ({primary_key_field}) DO NOTHING;"
#    print(insert_query)
    # put this command into a file  
    with open(output_file, "w") as f:
        f.write(insert_query)
    return insert_query

if __name__=="__main__":
    schema_sql = '/Users/sujatagoswami/Documents/LBL/UO_DATA/migrated_data/create_table_sql_files/Authors.sql'
    schema, table_name = extract_column_info(schema_sql)
    print("schema: ", schema)               
    print("table_name: ", table_name)

