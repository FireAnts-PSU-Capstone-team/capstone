from enum import Enum


class ColumnNames(Enum):
    ROW = 0
    SUBMISSION_DATE = 1
    ENTITY = 2
    DBA = 3
    FACILITY_ADDRESS = 4
    FACILITY_SUITE = 5
    FACILITY_ZIP = 6
    MAILING_ADDRESS = 7
    MRL = 8
    NEIGHBORHOOD_ASSN = 9
    COMPLIANCE_REGION = 10
    FIRST_NAME = 11
    LAST_NAME = 12
    EMAIL = 13
    PHONE = 14
    ENDORSE_TYPE = 15
    LICENSE_TYPE = 16
    REPEAT_LOCATION = 17
    APP_COMPLETE = 18
    FEE_SCHEDULE = 19
    RECEIPT_NUM = 20
    CASH_AMT = 21
    CHECK_AMT = 22
    CARD_AMT = 23
    CHECK_NUM = 24
    MRL_NUM = 25
    NOTES = 26


class IntakeRow:
    """
    Represents a row of the intake table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.row = None
        self.submission_date = ''
        self.entity = ''
        self.dba = ''
        self.facility_address = ''
        self.facility_suite = ''
        self.facility_zip = ''
        self.mailing_address = ''
        self.mrl = ''
        self.neighborhood_assn = ''
        self.compliance_region = ''
        self.first_name = ''
        self.last_name = ''
        self.email = ''
        self.phone = ''
        self.endorse_type = ''
        self.license_type = ''
        self.repeat_license = ''
        self.app_complete = ''
        self.fee_schedule = ''
        self.receipt_num = ''
        self.cash_amt = ''
        self.check_amt = ''
        self.card_amt = ''
        self.check_num = ''
        self.mrl_num = ''
        self.notes = ''

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the intake table
            
        """

        def check_to_exist(json, field):
            if field in json:
                return json.get(field)
            else:
                raise KeyError(f"Missing field: {field}")
        
        self.row = input_json.get('row')
        self.submission_date = check_to_exist(input_json,'Submission date')
        self.entity = check_to_exist(input_json, 'Entity')
        self.dba = check_to_exist(input_json,'DBA')
        self.facility_address = check_to_exist(input_json, 'Facility Address')
        self.facility_suite = check_to_exist(input_json, 'Facility Suite #')
        self.facility_zip = check_to_exist(input_json, 'Facility Zip')
        self.mailing_address = check_to_exist(input_json, 'Mailing Address')
        self.mrl = check_to_exist(input_json, 'MRL')
        self.neighborhood_assn = check_to_exist(input_json, 'Neighborhood Association')
        self.compliance_region = check_to_exist(input_json, 'Compliance Region')
        self.first_name = check_to_exist(input_json, 'Primary Contact Name (first)')
        self.last_name = check_to_exist(input_json, 'Primary Contact Name (last)')
        self.email = check_to_exist(input_json, 'Email')
        self.phone = check_to_exist(input_json, 'Phone')
        self.endorse_type = check_to_exist(input_json, 'Endorse Type')
        self.license_type = check_to_exist(input_json, 'License Type')
        self.repeat_license = check_to_exist(input_json, 'Repeat location?')
        self.app_complete = check_to_exist(input_json, 'App complete?')
        self.fee_schedule = check_to_exist(input_json, 'Fee Schedule')
        self.receipt_num = check_to_exist(input_json, 'Receipt No.')
        self.cash_amt = check_to_exist(input_json, 'Cash Amount')
        self.check_amt = check_to_exist(input_json, 'Check Amount')
        self.card_amt = check_to_exist(input_json, 'Card Amount')
        self.check_num = check_to_exist(input_json, 'Check No. / Approval Code')
        self.mrl_num = check_to_exist(input_json, 'MRL#')
        self.notes = check_to_exist(input_json, 'Notes')

    

    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.row, self.submission_date, self.entity, self.dba, self.facility_address, self.facility_suite,
                self.facility_zip, self.mailing_address, self.mrl, self.neighborhood_assn, self.compliance_region,
                self.first_name, self.last_name, self.email, self.phone, self.endorse_type, self.license_type,
                self.repeat_license, self.app_complete, self.fee_schedule, self.receipt_num, self.cash_amt,
                self.check_amt, self.card_amt, self.check_num, self.mrl_num, self.notes]
