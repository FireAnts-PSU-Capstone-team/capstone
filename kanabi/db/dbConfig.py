#!/usr/bin/python
from configparser import ConfigParser


def pgSqlConfig(filename='kanabi/db/database.ini', section='postgresql'):
    """
    Extracts configuration parameters from the .ini file
    Args:
        filename: file to parse
        section: section of the file to read, if multiple are present
    Returns: an object containing the config parameters
    """

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
