import psycopg2
import configparser
 
# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('config_local_macbook.ini')

def execute_sql_file(db_config, sql_file):
    """Reads and executes SQL commands from a file on a PostgreSQL database."""
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to the PostgreSQL database.")
        
        # Read the SQL file
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Execute SQL script
        cursor.execute(sql_script)
        
        # Commit and close connection
        conn.commit()
        cursor.close()
        conn.close()
        print("SQL script executed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# db_config = {
#     "dbname": "test_dbase",
#     "user": "admin",
#     "password": " ",
#     "host": "localhost",
#     "port": "5432"
# }
if __name__ == "__main__":
    db_config = {
        "dbname": config.get('Database', 'db_name'),
        "user": config.get('Database', 'db_user'),
        "password": config.get('Database', 'db_password'),
        "host": config.get('Database', 'db_host'),
        "port": config.get('Database', 'db_port')
    }
    create_sql_file = '/Users/sujatagoswami/Documents/LBL/UO_DATA/migrated_data/create_table_sql_files/Users.sql'
    execute_sql_file(db_config, create_sql_file)
    insert_sql_file = '/Users/sujatagoswami/Documents/LBL/UO_DATA/migrated_data/insert_sql_files/Users.sql'
    
    # execute_sql_file(db_config, create_sql_file)
    execute_sql_file(db_config, insert_sql_file)

