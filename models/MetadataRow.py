from enum import Enum


class ColumnNames(Enum):
    FILENAME = 0
    CREATOR = 1
    SIZE =2
    CREATED_DATE = 3
    LAST_MODIFIED_DATE = 4
    LAST_MODIFIED_BY = 5
    TITLE = 6
    ROWS = 7
    COLUMNS = 8

class MetadataRow:
    """
    Represents a row of the Metadata table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.filename = ''
        self.creator = ''
        self.size = None
        self.created_date = ''
        self.last_modified_date = ''
        self.last_modified_by = ''
        self.title = ''
        self.rows = ''
        self.columns = ''
        

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the intake table
        """
        self.filename = input_json.get('filename')
        self.creator = input_json.get('creator')
        self.size = input_json.get('size')
        self.created_date = input_json.get('created_date')
        self.last_modified_date = input_json.get('last_modified_date')
        self.last_modified_by = input_json.get('last_modified_by')
        self.title = input_json.get('title')
        self.rows = input_json.get('rows')
        self.columns = input_json.get('columns')
        
        
    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.filename, self.creator, self.size, self.created_date, self.last_modified_date, self.last_modified_by,self.title,self.rows, self.columns]

