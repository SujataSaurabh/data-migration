from generate_create_table_sql import generate_create_table_sql
from generate_insert_sql import generate_insert_sql
from export_as_csv import sql_insert_to_csv
import configparser
import glob
import os
import traceback

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('config_local_macbook.ini')

#  main file to run the data migration
if __name__ == "__main__":
    excluded_tables = ['(TempProposalsAndBeamlines)', '(InternalFlag)','PXRapidAccess', 'PGIForms', 'AwardsTalks', 'BadgeReader', 'BadgesOLD', 'BeamlineUsage', 'BeamShifts', 'BioForms', 'Courses'
                       'EmailMessageLog', 'ESAFLog', 'ESSForms', 'EXPActionLog', 'ExpActionsOLD', 'ExpDatesOLD', 'ExperimentOLD', 'ExperimentSchedule',  'ExpPubs', 'FundingSources', 'Invoices', 
                       'Mailings', 'NightlyJobs', 'NightlyJobsLog', 'PeopleWEBOLD', 'ProposalReview', 'ProposalsOLD','RemoteUsers', 'ReservationsOLD', 'ReviewPeriodicals', 'RoomEventsOLD','Test_Table_Department', 'Test_Table_Employee',  'UserProfileForms', 'VoteCandidates', 'VoteResults', 'Workshops']

    ## Generate schema SQL
    input_schema_file = config.get('InputFiles', '4d_schema_file')
    schema_sql_path= config.get('OutputFiles', 'schema_sql_output_path')
    if not os.path.exists(schema_sql_path):
        os.makedirs(schema_sql_path)
    
    generate_create_table_sql(input_schema_file, schema_sql_path)

    # # Generate insert data to CSV
    print("Generating insert data to csv")

    input_data_path = config.get('InputFiles', '4d_data_path')
    output_data_path = config.get('OutputFiles', 'csv_file_output_path')
    
    if not os.path.exists(output_data_path):
        os.makedirs(output_data_path)

    for filename in glob.iglob(input_data_path + '**/Export.sql', recursive=True):
        # Extract the table name (e.g., VoteResults) from the file path
        table_name = os.path.basename(os.path.dirname(filename))
        print("table_name: ", table_name, "in csvf folder")
        # if table_name != 'Publications':
        #     continue
        if table_name in excluded_tables:
            continue
        if not os.path.exists(output_data_path + table_name + '.csv'):
            try:
                sql_insert_to_csv(filename, output_data_path)
            except Exception as e:
                print(f"An error occurred in table: {table_name} : {e}")
                print(traceback.format_exc())
        
    print("Generating insert data SQL") 
    insert_sql_path = config.get('OutputFiles', 'insert_sql_output_path')
    if not os.path.exists(insert_sql_path):
        os.makedirs(insert_sql_path)

    
    for filename in glob.iglob(output_data_path + '*.csv'):
        table_name = os.path.splitext(os.path.basename(filename))[0]
        print("table_name: ", table_name, "in SQL folder")
        if table_name != 'Users':
            continue
        if table_name in excluded_tables:
            continue
        table_schema = schema_sql_path + table_name + '.sql'
        output_file = insert_sql_path + table_name + '.sql'
        
        # generate_insert_sql(filename, table_schema, output_file)
        
        if not os.path.exists(output_file):
            try:
                generate_insert_sql(filename, table_schema, output_file)
            except Exception as e:
                print(f"An error occurred in table: {table_name} : {e}")
                print(traceback.format_exc())

