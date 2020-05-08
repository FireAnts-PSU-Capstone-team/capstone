class ArchiveRow:
    """
    Represents a row of the Archive table.
    """

    def __init__(self):
        """
        Default constructor.
        """
        self.row = None
        self.old_row = None
        self.old_submission_date = ''
        self.old_entity = ''
        self.old_dba = ''
        self.old_facility_address = ''
        self.old_facility_suite = ''
        self.old_facility_zip = ''
        self.old_mailing_address = ''
        self.old_mrl = ''
        self.old_neighborhood_association = ''
        self.old_compliance_region = ''
        self.old_primary_contact_first_name = ''
        self.old_primary_contact_last_name = ''
        self.old_email = ''
        self.old_phone = ''
        self.old_endorse_type = ''
        self.old_license_type = ''
        self.old_repeat_license = ''
        self.old_app_complete = ''
        self.old_fee_schedule = ''
        self.old_receipt_num = ''
        self.old_cash_amount = ''
        self.old_check_amount = ''
        self.old_card_amount = ''
        self.old_check_num = ''
        self.old_mrl_num = ''
        self.old_notes = ''

    def __init__(self, input_json):
        """
        Constructor from a JSON object. Any unsupplied data defaults to None
        Args:
            input_json ({}): JSON object representing a row of the archive table
        """
        self.row = input_json.get('row')
        self.old_row = input_json.get('old_row')
        self.old_submission_date = input_json.get('old_submission_date')
        self.old_entity = input_json.get('old_entity')
        self.old_dba = input_json.get('old_dba')
        self.old_facility_address = input_json.get('old_facility_address')
        self.old_facility_suite = input_json.get('old_facility_suite')
        self.old_facility_zip = input_json.get('old_facility_zip')
        self.old_mailing_address = input_json.get('old_ailing_address')
        self.old_mrl = input_json.get('old_mrl')
        self.old_neighborhood_association = input_json.get('old_neighborhood_association')
        self.old_compliance_region = input_json.get('old_compliance_region')
        self.old_primary_contact_first_name = input_json.get('old_primary_contact_first_name')
        self.old_primary_contact_last_name = input_json.get('old_primary_contact_last_name')
        self.old_email = input_json.get('old_email')
        self.old_phone = input_json.get('old_phone')
        self.old_endorse_type = input_json.get('old_endorse_type')
        self.old_license_type = input_json.get('old_license_type')
        self.old_repeat_license = input_json.get('old_repeat_location')
        self.old_app_complete = input_json.get('old_app_complete')
        self.old_fee_schedule = input_json.get('old_fee_schedule')
        self.old_receipt_num = input_json.get('old_receipt_num')
        self.old_cash_amount = input_json.get('old_cash_amount')
        self.old_check_amount = input_json.get('old_check_amount')
        self.old_card_amount = input_json.get('old_card_amount')
        self.old_check_num = input_json.get('old_check_num_approval_code')
        self.old_mrl_num = input_json.get('old_mrl_num')
        self.old_notes = input_json.get('old_notes')

