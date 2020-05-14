from enum import Enum


class ColNames(Enum):
    ID = 0
    TSTAMP = 1
    SCHEMANAME = 2
    OEPRATION = 3
    WHO = 4
    NEW_VAL = 5
    OLD_VAL = 6
    TABNAME = 7

class TxnHistoryRow:
    """
    Represents a row of the Txn_History table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.id = None
        self.tstamp = ''
        self.schemaname = ''
        self.operation = ''
        self.who = ''
        self.new_val = ''
        self.old_val = ''
        self.tabname = ''
        

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the txn_history table
        """
        self.id = input_json.get('id')
        self.tstamp = input_json.get('tstamp')
        self.schemaname = input_json.get('schemaname')
        self.operation = input_json.get('operation')
        self.who = input_json.get('who')
        self.new_val = input_json.get('new_val')
        self.old_val = input_json.get('old_val')
        self.tabname = input_json.get('tabname')
