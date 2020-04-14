class ArchiveRow:
    """
    Represents a row of the Archive table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.old_row = None
        self.old_submission_date = ''
        self.old_entity = ''
        self.old_dba = ''
        self.old_facility_address = ''
        self.old_facility_suite = ''
        self.old_facility_zip = ''
        self.old_mailing_address = ''
        self.old_mrl = ''
        self.old_neighborhood_assn = ''
        self.old_compliance_region = ''
        self.old_first_name = ''
        self.old_last_name = ''
        self.old_email = ''
        self.old_phone = ''
        self.old_endorse_type = ''
        self.old_license_type = ''
        self.old_repeat_license = ''
        self.old_app_complete = ''
        self.old_fee_schedule = ''
        self.old_receipt_num = ''
        self.old_cash_amt = ''
        self.old_check_amt = ''
        self.old_card_amt = ''
        self.old_check_num = ''
        self.old_mrl_num = ''
        self.old_notes = ''

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the archive table
        """
        self.old_row = input_json.get('row')
        self.old_submission_date = input_json.get('Submission date')
        self.old_entity = input_json.get('Entity')
        self.old_dba = input_json.get('DBA')
        self.old_facility_address = input_json.get('Facility Address')
        self.old_facility_suite = input_json.get('Facility Suite #')
        self.old_facility_zip = input_json.get('Facility Zip')
        self.old_mailing_address = input_json.get('Mailing Address')
        self.old_mrl = input_json.get('MRL')
        self.old_neighborhood_assn = input_json.get('Neighborhood Association')
        self.old_compliance_region = input_json.get('Compliance Region')
        self.old_first_name = input_json.get('Primary Contact First Name')
        self.old_last_name = input_json.get('Primary Contact Last Name')
        self.old_email = input_json.get('Email')
        self.old_phone = input_json.get('Phone')
        self.old_endorse_type = input_json.get('Endorse Type')
        self.old_license_type = input_json.get('License Type')
        self.old_repeat_license = input_json.get('Repeat location?')
        self.old_app_complete = input_json.get('App complete?')
        self.old_fee_schedule = input_json.get('Fee Schedule')
        self.old_receipt_num = input_json.get('Receipt No.')
        self.old_cash_amt = input_json.get('Cash Amount')
        self.old_check_amt = input_json.get('Check Amount')
        self.old_card_amt = input_json.get('Card Amount')
        self.old_check_num = input_json.get('Check No. / Approval Code')
        self.old_mrl_num = input_json.get('MRL#')
        self.old_notes = input_json.get('Notes')


