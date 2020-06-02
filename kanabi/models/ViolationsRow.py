from enum import Enum


class ColNames(Enum):
    ROW = 0
    DBA = 1
    ADDRESS = 2
    MRL = 3
    LICENSE_TYPE = 4
    VIOLATION_SENT_DATE = 5
    ORIGINAL_VIOLATION_AMOUNT = 6
    ADMIN_RVW_DECISION_DATE = 7
    ADMIN_RVW_VIOLATION_AMOUNT = 8
    CERTIFIED_NUM = 9
    CERTIFIED_RECEIPT_RETURNED = 10
    DATE_PAID_WAIVED = 11
    RECEIPT_NUM = 12
    CASH_AMT = 13
    CHECK_AMT = 14
    CARD_AMT = 15
    CHECK_NUM = 16
    NOTES = 17
    VALIDATION_ERRORS = 18


class ViolationsRow:
    """
    Represents a row of the violations table.
    """

    __slots__ = [
        'row',
        'dba',
        'address',
        'mrl',
        'license_type',
        'violation_sent_date',
        'original_violation_amount',
        'admin_rvw_decision_date',
        'admin_rvw_violation_amount',
        'certified_num',
        'certified_receipt_returned',
        'date_paid_waived',
        'receipt_no',
        'cash_amt',
        'check_amt',
        'card_amt',
        'check_num',
        'notes',
        'validation_errors'
    ]

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the intake table
        """
        self.row = input_json.get('row')
        self.dba = input_json.get('DBA')
        self.address = input_json.get('Address')
        self.mrl = input_json.get('MRL#')
        self.license_type = input_json.get('License Type')
        self.violation_sent_date = input_json.get('Violation sent date')
        self.original_violation_amount = input_json.get('Original Violation Amount')
        self.admin_rvw_decision_date = input_json.get('Admin Rvw Decision Date')
        self.admin_rvw_violation_amount = input_json.get('Admin Rvw Violation Amount')
        self.certified_num = input_json.get('Certified #')
        self.certified_receipt_returned = input_json.get('Certified receipt returned')
        self.date_paid_waived = input_json.get('Date paid/ Waived')
        self.receipt_no = input_json.get('Receipt No.')
        self.cash_amt = input_json.get('Cash Amount')
        self.check_amt = input_json.get('Check Amount')
        self.card_amt = input_json.get('Card Amount')
        self.check_num = input_json.get('Check No. / Approval Code')
        self.notes = input_json.get('Notes')

    def value_array(self):
        """
        Order data into an array that can be consumed by the row insertion method.
        Returns ([]): array of data members
        """
        return [self.row, self.dba, self.address, self.mrl, self.license_type, self.violation_sent_date,
                self.original_violation_amount, self.admin_rvw_decision_date, self.admin_rvw_violation_amount,
                self.certified_num, self.certified_receipt_returned,
                self.date_paid_waived, self.receipt_no, self.cash_amt,
                self.check_amt, self.card_amt, self.check_num, self.notes]
