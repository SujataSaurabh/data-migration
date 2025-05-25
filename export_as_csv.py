import csv
import re
import os

def split_excluding_quoted_parentheses(s):
    result = []
    current_row = []
    current_part = []
    inside_quotes = False  # Track whether we're inside single quotes
    inside_row = False  # Track whether we're inside parentheses

    for char in s:
        if char == "'":
            inside_quotes = not inside_quotes  # Toggle quote state
        elif inside_quotes:
            current_part.append(char)
        elif char == '(':
            inside_row = True
        elif char == ')':
            inside_row = False
            if current_part:
                current_row.append(''.join(current_part).strip())
                current_part = []
            if not current_row[0].startswith("["):
                result.append(current_row)
    #            print("current_row (",len(current_row),"): ", '|'.join(current_row))
            current_row = []
        elif inside_row and char == ',':
                current_row.append(''.join(current_part).strip().replace('\0', '')) # Remove null characters 
                current_part = []
        elif inside_row:
            current_part.append(char)
    return result


def sql_insert_to_csv(sql_file, output_dir):
    if not os.path.isfile(sql_file):
        print(f"Error: '{sql_file}' is not a valid file path.")
        return
    
    with open(sql_file, 'r', encoding='utf-8') as file:
        sql_query = file.read()
    
    # Extract table name
    table_match = re.search(r'INSERT INTO \[?(\w+)\]?\s*\((.*?)\)\s*VALUES\s*(.*);', sql_query, re.DOTALL)
    
    if not table_match:
        print("Invalid SQL query format")
        return
    
    table_name = table_match.group(1)  # Extract table name
    columns = [col.strip().strip('[]') for col in table_match.group(2).split(',')]  # Extract column names
    values_section = table_match.group(3).strip()
    
    rows = split_excluding_quoted_parentheses(values_section)
    csv_filename = output_dir + f"{table_name}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)  # Write column names
        writer.writerows(rows)   # Write values
    
    print(f"CSV file '{csv_filename}' created successfully.")
