import psycopg2
from .dbConfig import pgSqlConfig


def pg_connect():
    """
    Connect to the PostgreSQL database server.
    Returns: the database cursor and connection objects
    """
    try:
        # read connection parameters
        params = pgSqlConfig()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        conn.commit()
        return cur, conn
    # TODO: validate the exceptions thrown here, no reason to catch Exception and something else
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def pg_disconnect(cur, conn):
    """
    Breaks the database connection.
    Args:
        cur: database cursor
        conn: database connection object
    Returns: None
    """
    try:
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
