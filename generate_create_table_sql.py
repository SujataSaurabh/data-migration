import xml.etree.ElementTree as ET

def fourD_datatypes():
    {
        "1": "Boolean",
        "2": " ", 
        "3": "Integer", 
        "4": "Long Integer", 
        "5": " ",
        "6": "Real", 
        "7": " ",
        "8": "Date", 
        "9": "Time", 
        "10": "Text",
        "11": " ",
        "12": "Picture",
        "18":"BLOB"
    }

def parse_field_type_mssql(field_type):
    """Converts the XML type to MSSQL data type."""
    field_type_map = {
        "1": "BIT", # 4-D Boolean
        "3": "INT",  # 4-D Integer - Shorts values (2-byte Integer), i.e. in the range -32,768..32,767 (2^15..(2^15)-1)
        "4": "INT", # 4-D Long Integer -  -2^31..(2^31)-1 (4-byte Integer)
        "6": "REAL", # 4-D Real - Real data type is ±1.7e±308 (13 significant digits).
        "8": "DATE", # 4-D Date
        "9": "TIME", # 4-D Time
        "10": "NVARCHAR", # 4-D Text
        "12": "VARBINARY", # 4-D Picture
        "18":"VARBINARY" # 4-D Blob
    }
    return field_type_map.get(field_type, "NVARCHAR")

def parse_field_type_postgresql(field_type):
    """Converts the XML type to POSTGRESQL data type."""
    field_type_map = {
        "1": "boolean", # 4-D Boolean
        "3": "smallint",  # 4-D Integer - Shorts values (2-byte Integer), i.e. in the range -32,768..32,767 (2^15..(2^15)-1)
        "4": "integer", # 4-D Long Integer -  -2^31..(2^31)-1 (4-byte Integer)
        "6": "double precision", # 4-D Real - Real data type is ±1.7e±308 (13 significant digits).
        "8": "date", # 4-D Date
        "9": "time", # 4-D Time
        "10": "varchar", # 4-D Text to varchar because text is unlimited
        "12": "bytea", # 4-D Picture
        "18":"bytea" # 4-D Blob
    }
    return field_type_map.get(field_type, "text")

def update_fields(fields):
    """Updates the 4D field name with the naming conventions consistent with postgreSQL types."""
    field_map = {
        "Order": "Order_",
        "Proposal Cycle": "ProposalCycle",
        "First Beamlines": "FirstBeamlines",
        "First Beamline": "FirstBeamline",
        "Primary": "PrimaryReviewer",
        "User ID": "UserID",
        "First Name": "FirstName",
        "Last Name": "LastName",
        "Access Level": "AccessLevel",
        "Unused 1": "Unused1",
        "Unused 2": "Unused2",
        "Unused 3": "Unused3",
        "Unused 4": "Unused4",
        "Unused 5": "Unused5",
        "Unused 6": "Unused6",
        "Conference Code": "ConferenceCode",
        "Paper Copy": "PaperCopy",
        "Date Submitted": "DateSubmitted", 
        "High Degree": "HighDegree",
        "Safety Video": "SafetyVideo",
        "FVA Local Approval Date": "FVALocalApprovalDate",
        "Date visa letter sent": "DateVisaLetterSent",
        "Local Zip": "LocalZip",
        "Local Contact": "LocalContact",
        "Long Element": "LongElement",
        "BLS Shifts": "BLSShifts",
        "DD Shifts": "DDShifts"
    }
    return [field_map.get(field, field) for field in fields]
# 
def read_4d_schema(input_xml_file):
    """Reads the 4D schema XML file and returns the schema."""
    try:
        tree = ET.parse(input_xml_file)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

def generate_create_table_sql(input_xml_file, output_sql_file):
    """Reads schema file and generates CREATE TABLE SQL statements."""
    
    num_tables = 0
    try:
        root = read_4d_schema(input_xml_file)
        database_name = root.attrib.get("name", "Database")
        print(f"Generating SQL Script for Database: {database_name}\n")

        for table in root.findall("table"):
            output_sql_commands= []
 
            table_name = table.attrib["name"]
            num_tables += 1
            if table_name != "Proposals" :  # Skip tables without a name
                continue
            print(f"Processing table: {table_name}")
            fields = table.findall("field")

            sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"

            # Process fields
            for field in fields:
                field_name = field.attrib["name"]
                field_type = parse_field_type_postgresql(field.attrib["type"])
                length = field.attrib.get("limiting_length", "")
                never_null = field.attrib.get("never_null", "false") == "true"
                print(f"field_type = {field_type}")       
                print(f"never_null = {never_null}")  
                field_name = update_fields([field_name])[
                    0]  # Update field name with naming conventions
                # print(f"field_name = {field_name}")
                # Add length to NVARCHAR fields
                if field_type == "NVARCHAR" and length:
                    field_type += f"({length})"


                sql += f"    {field_name} {field_type}"
                if never_null:
                    sql += " NOT NULL"
                sql += ",\n"

            # Process primary key
            primary_key = table.find("primary_key")
            if primary_key is not None:
                primary_field_name = primary_key.attrib["field_name"]
                sql += f"    PRIMARY KEY ({primary_field_name}),\n"

            # Remove trailing comma
            sql = sql.rstrip(",\n") + "\n);\n"
            output_sql_commands.append(sql)
            
            # file generation and writing to file
            file_name = f"{table_name}.sql"
            write_to_file(output_sql_commands, output_sql_file+file_name)
            print(f"SQL file generated: {file_name}")
        print(f"Total tables processed: {num_tables}")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_to_file(output_sql_commands, output_sql_file):
    """Writes the SQL commands to a file."""
    destimation_file = output_sql_file  
    with open(destimation_file, "w") as f:
        for sql_command in output_sql_commands:
            f.write(sql_command + "\n\n")
    print(f"SQL commands written to: {destimation_file}")
# Example usage


if __name__ == "__main__":
    input_xml_file = '/Users/sujatagoswami/Documents/rsync_macMini/catalog.4DCatalog'
    output_sql_file = '/Users/sujatagoswami/Documents/LBL/UO_DATA/migrated_data/create_table_sql_files/'
    generate_create_table_sql(input_xml_file, output_sql_file)

