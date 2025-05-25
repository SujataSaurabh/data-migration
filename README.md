# Data Migration Application
This application migrates data from a 4D database to PostgreSQL, handling schema conversion, data transformation, and special character processing.

## Prerequisites

- Python 3.x
- PostgreSQL database
- Access to 4D database export files
- macOS (for scheduled tasks)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd data_migration
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a configuration file `config_local_macbook.ini` with the following structure:
```ini
[General]
debug = True
log_level = info

[Database]
db_name = your_database_name
db_user = your_database_user
db_password = your_database_password
db_host = localhost
db_port = 5432

[InputFiles]
4d_schema_file = /path/to/your/catalog.4DCatalog
4d_data_path = /path/to/your/4d_export_data/

[OutputFiles]
schema_sql_output_path = /path/to/output/schema_sql_files/
csv_file_output_path = /path/to/output/csv_files/
insert_sql_output_path = /path/to/output/insert_sql_files/
```

## Project Structure

```
data_migration/
├── data_migration_app.py      # Main application file
├── generate_create_table_sql.py # Schema conversion
├── generate_insert_sql.py     # SQL insert generation
├── export_as_csv.py          # CSV export functionality
├── unicode_converter.py      # Special character handling
├── run_data_migration.sh     # Shell script for automation
├── config_local_macbook.ini  # Configuration file
└── logs/                     # Log directory
```

## Running the Application

### Manual Execution

1. Make the shell script executable:
```bash
chmod +x run_data_migration.sh
```

2. Run the migration script:
```bash
./run_data_migration.sh
```

### Automated Monthly Execution

1. Set up a cron job to run monthly:
```bash
crontab -e
```

2. Add the following line to run on the first day of each month at 2 AM:
```
0 2 1 * * /full/path/to/run_data_migration.sh
```

## Email Notifications

The application sends email notifications to sujata.saur@gmail.com for:
- Successful completion
- Failed migrations
- Configuration errors
- Missing file errors

## Logging

- Logs are stored in the `logs/` directory
- Each run creates a new log file with the date: `data_migration_YYYY-MM-DD.log`
- Logs include timestamps and detailed error messages

## Troubleshooting

1. **Database Connection Issues**
   - Verify database credentials in config file
   - Ensure PostgreSQL is running
   - Check network connectivity

2. **File Permission Issues**
   - Ensure read access to input files
   - Ensure write access to output directories
   - Check execute permissions on shell script

3. **Email Notification Issues**
   - Verify mail command is installed: `which mail`
   - Check email configuration
   - Verify email address is correct in script

4. **Python Package Issues**
   - Verify all required packages are installed
   - Check Python version compatibility

## Maintenance

1. **Regular Checks**
   - Monitor log files for errors
   - Verify database updates
   - Check disk space for output files

2. **Backup**
   - Keep backup of configuration file
   - Archive old log files
   - Backup database before major updates

## Support

For issues or questions, contact:
- Email: sujata.saur@gmail.com

## License

[Add your license information here] 