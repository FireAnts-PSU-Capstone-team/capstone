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
        self.row = input_json.get('row')
        self.submission_date = input_json.get('Submission date')
        self.entity = input_json.get('Entity')
        self.dba = input_json.get('DBA')
        self.facility_address = input_json.get('Facility Address')
        self.facility_suite = input_json.get('Facility Suite #')
        self.facility_zip = input_json.get('Facility Zip')
        self.mailing_address = input_json.get('Mailing Address')
        self.mrl = input_json.get('MRL')
        self.neighborhood_assn = input_json.get('Neighborhood Association')
        self.compliance_region = input_json.get('Compliance Region')
        self.first_name = input_json.get('Primary Contact First Name')
        self.last_name = input_json.get('Primary Contact Last Name')
        self.email = input_json.get('Email')
        self.phone = input_json.get('Phone')
        self.endorse_type = input_json.get('Endorse Type')
        self.license_type = input_json.get('License Type')
        self.repeat_license = input_json.get('Repeat location?')
        self.app_complete = input_json.get('App complete?')
        self.fee_schedule = input_json.get('Fee Schedule')
        self.receipt_num = input_json.get('Receipt No.')
        self.cash_amt = input_json.get('Cash Amount')
        self.check_amt = input_json.get('Check Amount')
        self.card_amt = input_json.get('Card Amount')
        self.check_num = input_json.get('Check No. / Approval Code')
        self.mrl_num = input_json.get('MRL#')
        self.notes = input_json.get('Notes')

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
