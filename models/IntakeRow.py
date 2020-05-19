from enum import Enum


class ColNames(Enum):
    ROW = 0
    SUBMISSION_DATE = 1
    ENTITY = 2
    DBA = 3
    FACILITY_ADDRESS = 4
    FACILITY_SUITE = 5
    FACILITY_ZIP = 6
    MAILING_ADDRESS = 7
    MRL = 8
    NEIGHBORHOOD_ASSOCIATION = 9
    COMPLIANCE_REGION = 10
    PRIMARY_CONTACT_FIRST_NAME = 11
    PRIMARY_CONTACT_LAST_NAME = 12
    EMAIL = 13
    PHONE = 14
    ENDORSE_TYPE = 15
    LICENSE_TYPE = 16
    REPEAT_LOCATION = 17
    APP_COMPLETE = 18
    FEE_SCHEDULE = 19
    RECEIPT_NUM = 20
    CASH_AMOUNT = 21
    CHECK_AMOUNT = 22
    CARD_AMOUNT = 23
    CHECK_NUM_APPROVAL_CODE = 24
    MRL_NUM = 25
    NOTES = 26


intake_headers = ['Submission date', 'Entity', 'DBA', 'Facility Address', 'Facility Suite #', 'Facility Zip',
                  'Mailing Address', 'MRL', 'Neighborhood Association', 'Compliance Region',
                  'Primary Contact Name (first)', 'Primary Contact Name (last)', 'Email', 'Phone', 'Endorse Type',
                  'License Type', 'Repeat location?', 'App complete?', 'Fee Schedule', 'Receipt No.', 'Cash Amount',
                  'Check Amount', 'Card Amount', 'Check No. / Approval Code', 'MRL#', 'Notes']


class IntakeRow:
    """
    Represents a row of the intake table.
    """

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

        self.ROW = input_json.get('ROW')
        self.SUBMISSION_DATE = check_to_exist(input_json, 'SUBMISSION DATE')
        self.ENTITY = check_to_exist(input_json, 'ENTITY')
        self.DBA = check_to_exist(input_json, 'DBA')
        self.FACILITY_ADDRESS = check_to_exist(input_json, 'FACILITY ADDRESS')
        self.FACILITY_SUITE = check_to_exist(input_json, 'FACILITY SUITE #')
        self.FACILITY_ZIP = check_to_exist(input_json, 'FACILITY ZIP')
        self.MAILING_ADDRESS = check_to_exist(input_json, 'MAILING ADDRESS')
        self.MRL = check_to_exist(input_json, 'MRL')
        self.NEIGHBORHOOD_ASSOCIATION = check_to_exist(input_json, 'NEIGHBORHOOD ASSOCIATION')
        self.COMPLIANCE_REGION = check_to_exist(input_json, 'COMPLIANCE REGION')
        self.PRIMARY_CONTACT_FIRST_NAME = check_to_exist(input_json, 'PRIMARY_CONTACT_FIRST_NAME')
        self.PRIMARY_CONTACT_LAST_NAME = check_to_exist(input_json, 'PRIMARY_CONTACT_LAST_NAME')
        self.EMAIL = check_to_exist(input_json, 'EMAIL')
        self.PHONE = check_to_exist(input_json, 'PHONE')
        self.ENDORSE_TYPE = check_to_exist(input_json, 'ENDORSE_TYPE')
        self.LICENSE_TYPE = check_to_exist(input_json, 'LICENSE_TYPE')
        self.REPEAT_LICENSE = check_to_exist(input_json, 'REPEAT_L0CATION')
        self.APP_COMPLETE = check_to_exist(input_json, 'APP_COMPLETE')
        self.FEE_SCHEDULE = check_to_exist(input_json, 'FEE_SCHEDULE')
        self.RECEIPT_NUM = check_to_exist(input_json, 'RECEIPT_NUM')
        self.CASH_AMOUNT = check_to_exist(input_json, 'CASH_AMOUNT')
        self.CHECK_AMOUNT = check_to_exist(input_json, 'CHECK_AMOUNT')
        self.CARD_AMOUNT = check_to_exist(input_json, 'CARD_AMOUNT')
        self.CHECK_NUM = check_to_exist(input_json, 'CHECK_NUM')
        self.MRL_NUM = check_to_exist(input_json, 'MRL_NUM')
        self.NOTES = check_to_exist(input_json, 'NOTES')

    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.ROW, self.SUBMISSION_DATE, self.ENTITY, self.DBA, self.FACILITY_ADDRESS, self.FACILITY_SUITE,
                self.FACILITY_ZIP, self.MAILING_ADDRESS, self.MRL, self.NEIGHBORHOOD_ASSOCIATION,
                self.COMPLIANCE_REGION,
                self.PRIMARY_CONTACT_FIRST_NAME, self.PRIMARY_CONTACT_LAST_NAME, self.EMAIL, self.PHONE,
                self.ENDORSE_TYPE, self.LICENSE_TYPE,
                self.REPEAT_LICENSE, self.APP_COMPLETE, self.FEE_SCHEDULE, self.RECEIPT_NUM, self.CASH_AMOUNT,
                self.CHECK_AMOUNT, self.CARD_AMOUNT, self.CHECK_NUM, self.MRL_NUM, self.NOTES]
