#!/bin/bash

# Set the working directory to the script's location
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current date for log file
DATE=$(date +"%Y-%m-%d")
LOG_FILE="logs/data_migration_${DATE}.log"

# Email settings
EMAIL_TO="sujata.saur@gmail.com"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Start logging
log_message "Starting data migration process"

# Check if config file exists
if [ ! -f "config_local_macbook.ini" ]; then
    log_message "Error: config_local_macbook.ini not found"
    mail -s "Data Migration Error: Config File Missing" "$EMAIL_TO" < "$LOG_FILE"
    exit 1
fi

# Check if required Python files exist
required_files=("data_migration_app.py" "generate_create_table_sql.py" "generate_insert_sql.py" "export_as_csv.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        log_message "Error: Required file $file not found"
        mail -s "Data Migration Error: Missing Required File" "$EMAIL_TO" < "$LOG_FILE"
        exit 1
    fi
done

# Run the Python script and capture both stdout and stderr
log_message "Executing data migration script"
python3 data_migration_app.py >> "$LOG_FILE" 2>&1

# Check if the script executed successfully
if [ $? -eq 0 ]; then
    log_message "Data migration completed successfully"
    mail -s "Data Migration Completed Successfully" "$EMAIL_TO" < "$LOG_FILE"
else
    log_message "Error: Data migration failed"
    mail -s "Data Migration Failed" "$EMAIL_TO" < "$LOG_FILE"
    exit 1
fi

# Log completion
log_message "Data migration process completed" 