import pandas as pd
import numpy as np
import psycopg2

import connection as c
import os
import sys
import time
from openpyxl import load_workbook


test_file = 'files/sample.xlsx'
primary_table = 'intake'
metadata_table = 'metadata'

is_connected = False
wait_time = 0
while not is_connected:
    try:
        pgSqlCur, pgSqlConn = c.pg_connect()
        is_connected = True
    except:
        time.sleep(1)
        wait_time += 1
        sys.stdout.write(f'\rConnecting to DB ... {wait_time}')


def fmt(s):
    """
    Formats an input element for SQL-friendly injection. Translates None to "NULL", quotes strings, and stringifies
    non-textual arguments.
    Args:
        s: the input element
    Returns (str): a SQL-friendly string representation
    """
    if s is None or str(s).lower() == 'nan':
        s = "NULL"
    else:
        if type(s) is str:
            s = "'" + str(s).replace('"', '').replace("'", "") + "'"  # strip quotation marks
        else:
            s = str(s)
    return s


def dump_tables():
    """
    Displays the contents of the tables in the database.
    Returns: None
    """
    print("Test:\n-------------------------------")
    pgSqlCur.execute(f"select * from {primary_table}")
    rows = pgSqlCur.fetchall()
    for row in rows:
        print(row)

    print("\nMetadata:\n-------------------------------")
    pgSqlCur.execute("select * from metadata")
    rows = pgSqlCur.fetchall()
    for row in rows:
        print(row)
        
        
def table_exists(cur, table):
    """
    Checks whether the named table exists.
    Args:
        cur ({}): the Postgres cursor
        table (str): the table to validate
    Returns (bool): whether the table was found

    """
    try:
        cur.execute("select exists(select relname from pg_class where relname='" + table + "')")
        exists = cur.fetchone()[0]

    except psycopg2.Error:
        exists = False

    return exists
        

# TODO: error handling
class InvalidTableException(Exception):
    """
    Thrown when the specified table does not exist.
    """
    pass


def get_table(table_name):
    """
    Return a JSON-like format of table data.
    Args:
        table_name: the table to fetch
    Returns ([str]): an object-notated dump of the table
    """
    result = []
    column_name = []

    if not table_exists(pgSqlCur, table_name):
        raise InvalidTableException
    
    pgSqlCur.execute(f'select * from {table_name}')
    rows = pgSqlCur.fetchall()
    
    for col in pgSqlCur.description:
        column_name.append(col.name)
    
    for row in rows:
        a_row = {}
        i = 0
        for col in column_name:
            a_row[col] = row[i]
            i += 1
        result.append(a_row)

    return result


# TODO: error handling
def read_metadata(f):
    """
    Collects metadata about a spreadsheet to be consumed.
    Args:
        f (str): the filename of the spreadsheet
    Returns (dict): the metadata collection
    """
    # TODO: add column and row counts, if possible
    data = {}
    workbook = load_workbook(f)
    file_data = workbook.properties.__dict__
    sheet_data = workbook.worksheets[0]
    os_data = os.stat(f)

    data['filename'] = fmt(os.path.basename(f))
    data['creator'] = fmt(file_data.get('creator'))
    data['size'] = os_data.st_size
    data['created'] = fmt(file_data.get('created').strftime('%Y-%m-%d %H:%M:%S+08'))
    data['modified'] = fmt(file_data.get('modified').strftime('%Y-%m-%d %H:%M:%S+08'))
    data['lastModifiedBy'] = fmt(file_data.get('lastModifiedBy'))
    data['title'] = fmt(file_data.get('title'))
    data['rows'] = sheet_data.max_row
    data['columns'] = sheet_data.max_column

    return data


# TODO: validate filename and respond without throwing
def load_spreadsheet(f):
    """
    Read the spreadsheet file into a dataframe object.
    Args:
        f (str): the filename of the spreadsheet to consume
        sheet_name (str): the worksheet to process within a larger file
    Returns (dataframe): extracted data
    """
    return pd.read_excel(f)


def write_info_data(df):
    """
    Write data from spreadsheet to the information table.
    Args:
        df (dataframe): data from spreadsheet
    Returns: None
    """
    row_array = np.ndenumerate(df.values).iter.base
    for row in row_array:
        insert_row(primary_table, row)


def write_metadata(metadata):
    """
    Write metadata of Excel file into metadata table.
    Args:
        metadata (dict): the metadata dictionary
    Returns: None
    """
    cmd = "INSERT INTO {}(filename, creator, size, created_date, last_modified_date, last_modified_by, title, rows, columns) " \
        "VALUES({},{},{},{},{},{},{}) ON CONFLICT DO NOTHING"
    pgSqlCur.execute(cmd.format(metadata_table, metadata['filename'], metadata['creator'], metadata['size'],
                                metadata['created'], metadata['modified'], metadata['lastModifiedBy'], metadata['title'],
                                metadata['rows'], metadata['columns']))


# TODO?: once tables are modeled as classes, change this function to take an iterable of the schema
# so we can insert into an arbitrary table
# TODO: revisit row sequencing; change "DEFAULT, then start from row[1]" to process entire row one way or another
def insert_row(table, row):
    """
    Insert an array of values into the specified table.
    Args:
        table (str): name of table to insert into
        row ([]): row of values to insert
    Returns: None

    """
    cmd = f"INSERT INTO {table} VALUES (DEFAULT"
    for i in range(1, len(row)):
        cmd += f", {fmt(row[i])}"
    cmd += ")"
    pgSqlCur.execute(cmd)


# TODO: catch exceptions and respond appropriately
def process_file(f):
    """
    Read an Excel file; put info data into info table, metadata into metadata table
    Args:
        f (str): filename of spreadsheet
    Returns (bool): True if successful, else False
    """

    # validate file exists
    if not os.path.exists(f):
        if os.path.exists('files/' + f):
            f = 'files/' + f
        else:
            return False

    # read file content
    df = load_spreadsheet(f)
    
    # Write the data to the DB
    write_info_data(df)

    # insert metadata into metadata table
    # should add version and revision to this schema, but don't know types yet
    metadata = read_metadata(f)
    
    write_metadata(metadata)

    # commit execution
    pgSqlConn.commit()

    return True


def test_driver():
    # Pre-insert query
    print('Dump tables -------------------------------------------------')
    dump_tables()

    print('\nInsert data -------------------------------------------------')
    process_file(test_file)

    # three options for collisions:
    # 1. do nothing (discard new row; probably want to return an error to the user in this case)
    # 2. update existing record with new metadata
    # ON CONFLICT (filename)
    #       DO UPDATE
    #       SET (size, last_modified_by, modified) = (EXCLUDED.size, EXCLUDED.last_modified_by, EXCLUDED.modified)
    # 3. add entirely new record
    # would need to return status of insertion, then insert a new row. Would need an incrementing column, like 'version'

    # unfortunately, it looks like 'creator' and 'created' are both fabricated by openpyxl, so we may need to find
    # a different way to capture that data if we want to keep them

    # Post insert query, verify data is inserted
    print('\nDump tables -------------------------------------------------')
    dump_tables()

    # close the db connection
    print("Closing connection to database.")
    c.pg_disconnect(pgSqlCur, pgSqlConn)
