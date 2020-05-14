from enum import Enum


class ColNames(Enum):
    ROW = 0
    TSTAMP = 1
    WHO = 2
    OLD_VAL = 3

class ArchiveRow:
    """
    Represents a row of the Archive table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.row = None
        self.tstamp = ''
        self.who =''
        self.old_val=''

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the archive table
        """
        self.row = input_json.get('row')
        self.tstamp = input_json.get('tstamp')
        self.who = input_json.get('who')
        self.old_val = input_json.get('old_val')


