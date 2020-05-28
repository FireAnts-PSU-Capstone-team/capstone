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
    VALIDATION_ERRORS = 27


intake_headers = ['Submission date', 'Entity', 'DBA', 'Facility Address', 'Facility Suite #', 'Facility Zip',
                  'Mailing Address', 'MRL', 'Neighborhood Association', 'Compliance Region',
                  'Primary Contact Name (first)', 'Primary Contact Name (last)', 'Email', 'Phone', 'Endorse Type',
                  'License Type', 'Repeat location?', 'App complete?', 'Fee Schedule', 'Receipt No.', 'Cash Amount',
                  'Check Amount', 'Card Amount', 'Check No. / Approval Code', 'MRL#', 'Notes']


class IntakeRow:
    """
    Represents a row of the intake table.
    """

    __slots__ = [
        'row',
        'submission_date',
        'entity',
        'dba',
        'facility_address',
        'facility_suite',
        'facility_zip',
        'mailing_address',
        'mrl',
        'neighborhood_association',
        'compliance_region',
        'primary_contact_first_name',
        'primary_contact_last_name',
        'email',
        'phone',
        'endorse_type',
        'license_type',
        'repeat_license',
        'app_complete',
        'fee_schedule',
        'receipt_num',
        'cash_amount',
        'check_amount',
        'card_amount',
        'check_num',
        'mrl_num',
        'notes',
        'validation_errors'
    ]

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
        self.submission_date = check_to_exist(input_json, 'Submission date')
        self.entity = check_to_exist(input_json, 'Entity')
        self.dba = check_to_exist(input_json, 'DBA')
        self.facility_address = check_to_exist(input_json, 'Facility Address')
        self.facility_suite = check_to_exist(input_json, 'Facility Suite #')
        self.facility_zip = check_to_exist(input_json, 'Facility Zip')
        self.mailing_address = check_to_exist(input_json, 'Mailing Address')
        self.mrl = check_to_exist(input_json, 'MRL')
        self.neighborhood_association = check_to_exist(input_json, 'Neighborhood Association')
        self.compliance_region = check_to_exist(input_json, 'Compliance Region')
        self.primary_contact_first_name = check_to_exist(input_json, 'Primary Contact Name (first)')
        self.primary_contact_last_name = check_to_exist(input_json, 'Primary Contact Name (last)')
        self.email = check_to_exist(input_json, 'Email')
        self.phone = check_to_exist(input_json, 'Phone')
        self.endorse_type = check_to_exist(input_json, 'Endorse Type')
        self.license_type = check_to_exist(input_json, 'License Type')
        self.repeat_license = check_to_exist(input_json, 'Repeat location?')
        self.app_complete = check_to_exist(input_json, 'App complete?')
        self.fee_schedule = check_to_exist(input_json, 'Fee Schedule')
        self.receipt_num = check_to_exist(input_json, 'Receipt No.')
        self.cash_amount = check_to_exist(input_json, 'Cash Amount')
        self.check_amount = check_to_exist(input_json, 'Check Amount')
        self.card_amount = check_to_exist(input_json, 'Card Amount')
        self.check_num = check_to_exist(input_json, 'Check No. / Approval Code')
        self.mrl_num = check_to_exist(input_json, 'MRL#')
        self.notes = check_to_exist(input_json, 'Notes')

    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.row, self.submission_date, self.entity, self.dba, self.facility_address, self.facility_suite,
                self.facility_zip, self.mailing_address, self.mrl, self.neighborhood_association,
                self.compliance_region,
                self.primary_contact_first_name, self.primary_contact_last_name, self.email, self.phone,
                self.endorse_type, self.license_type,
                self.repeat_license, self.app_complete, self.fee_schedule, self.receipt_num, self.cash_amount,
                self.check_amount, self.card_amount, self.check_num, self.mrl_num, self.notes]


def from_array(input_array: []) -> IntakeRow:
    ret = {}
    for i, h in enumerate(intake_headers):
        ret[h] = input_array[i]
    return IntakeRow(ret)


if __name__ == '__main__':
    row = {
        "Submission date": "01/01/18",
        "Entity": "The Greenhouse",
        "DBA": "Boss Nass's",
        "Facility Address": "197 N Electric Ave",
        "Facility Suite #": "",
        "Facility Zip": "97204",
        "Mailing Address": "100 NE Tabor Dr",
        "MRL": "MRL48",
        "Neighborhood Association": "Arbor Lodge",
        "Compliance Region": "SE",
        "Primary Contact Name (first)": "Ashley",
        "Primary Contact Name (last)": "Clark",
        "Email": "ac@example.com",
        "Phone": "971-245-0996",
        "Endorse Type": "EX,CT",
        "License Type": "MR",
        "Repeat location?": "N",
        "App complete?": "Y",
        "Fee Schedule": "2020",
        "Receipt No.": 67,
        "Cash Amount": "$1500",
        "Check Amount": "0",
        "Card Amount": "",
        "Check No. / Approval Code": "512",
        "MRL#": "MRL48",
        "Notes": ""
    }
    arr = IntakeRow(row).value_array()
    r = from_array(arr)
    for i in r.value_array():
        print(i)
