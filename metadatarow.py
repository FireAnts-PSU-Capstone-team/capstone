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
        
        
    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.filename, self.creator, self.size, self.created_date, self.last_modified_date, self.last_modified_by,self.title]

