from enum import Enum


class ColumnNames(Enum):
    ROW = 0
    DATE = 1
    METHOD = 2
    INTAKE_PERSON = 3
    RP_NAME = 4
    RP_CONTACT_INFO = 5
    CONCERN = 6
    LOCATION_NAME = 7
    LOCATION_ADDRESS = 8
    MRL = 9
    ACTION_TAKEN = 10
    STATUS = 11
    STATUS_DATE = 12
    ADDITIONAL_NOTES = 13


class ReportsRow:
    """
    Represents a row of the reports table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.row_id = None
        self.date = ''
        self.method = ''
        self.intake_person = ''
        self.rp_name = ''
        self.rp_contact_info = ''
        self.concern = ''
        self.location_name = ''
        self.location_address = ''
        self.mrl = ''
        self.action_taken = ''
        self.status = ''
        self.status_date = ''
        self.additional_notes = ''

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the intake table
        """
        self.row_id = input_json.get('row')
        self.date = input_json.get('Date')
        self.method = input_json.get('Method')
        self.intake_person = input_json.get('Intake Person')
        self.rp_name = input_json.get('RP (Name)')
        self.rp_contact_info = input_json.get('RP (Contact Info)')
        self.concern = input_json.get('Concern')
        self.location_name = input_json.get('Location Name')
        self.location_address = input_json.get('Location Address')
        self.mrl = input_json.get('MRL?')
        self.action_taken = input_json.get('Action Taken')
        self.status = input_json.get('Status')
        self.status_date = input_json.get('Status Date')
        self.additional_notes = input_json.get('Additional Notes')

    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.row_id, self.date, self.method, self.intake_person, self.rp_name, self.rp_contact_info,
                self.concern, self.location_name, self.location_address, self.mrl, self.action_taken,
                self.status, self.status_date, self.additional_notes]
