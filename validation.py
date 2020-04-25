import pandas as pd
import numpy as np
import re as re
from models.IntakeRow import RowNames

'''Regular expression translated: Any amount of integers but at least one, a space, a 1-2 letter word (for directions N, SW, etc)
    Followed by a space, followed by any number of letters/numbers (but at least one) followed by a space. 
    This is followed by a space, followed by a word (for the St., Ave., etc).
    This is difficult to maintain though!! Holy cow!'''
addressRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s([a-zA-Z0-9]+\s)([a-zA-Z]+)'
addressWithFacilityRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s(([a-zA-Z1-9]+\s)+)([a-zA-Z]+)\s(#\d+)'
POBoxRegex = r'^([P|p][O|o])\s(Box|box)\s(\d+)(\,)*(\s)[a-zA-Z1-9]+(\,)*\s[A-Z]{2}(\,)*\s\d{5}'
emailRegex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
repeat_location_values = ['Y', 'N', 'X', 'NAN']
app_complete_values = ['M', 'N', 'N/A', 'Y', 'NAN']

validNeighborhoods = ['Central Northeast Neighbors', 'Beaumont-Wilshire', 'Cully', 'Grant Park', 'Hollywood',
                      'Madison South', 'Rose City Park', 'Roseway', 'Sumner', 'Sunderland', 'East Portland',
                      'Argay Terrace', 'Centennial', 'Glenfair', 'Hazelwood', 'Lents', 'Mill Park', 'Parkrose Heights',
                      'Parkrose', 'Pleasant Valley', 'Powellhurst-Gilbert', 'Russell', 'Wilkes', 'Woodland Park',
                      'Northeast Coalition', 'Alameda', 'Boise', 'Concordia', 'Eliot', 'Humboldt', 'Irvington', 'King',
                      'Lloyd District', 'Sabin', "Sullivan's Gulch", 'Vernon', 'Woodlawn', 'Southeast Uplift',
                      'Ardenwald/Johnson Creek', 'Brentwood/Darlington', 'Brooklyn', 'Buckman', 'Creston-Kenilworth',
                      'Eastmoreland', 'Foster-Powell', 'Hosford-Abernethy', 'Kerns', 'Laurelhurst', 'Montavilla',
                      'Mt Scott-Arleta', 'Mt Tabor', 'North Tabor', 'Reed', 'Richmond', 'Sellwood-Moreland',
                      'South Tabor', 'Sunnyside', 'Woodstock', 'Arbor Lodge', 'Bridgeton', 'Cathedral Park',
                      'East Columbia', 'Hayden Island', 'Kenton', 'Overlook', 'Piedmont', 'Portsmouth', 'St Johns',
                      'University Park', 'Arlington Heights', 'Forest Park', 'Goosehollow Foothills', 'Hillside',
                      'Linnton', 'Northwest District', 'Northwest Heights', 'Old Town', 'Pearl District',
                      'Portland Downtown', 'Sylvan-Highlands', 'Southwest Neighborhood Inc', 'Arnold Creek', 'Ashcreek',
                      'Bridlemile', 'Collins View', 'Crestwood', 'Far Southwest', 'Hayhurst', 'Healy Heights',
                      'Hillsdale', 'Homestead', 'Maplewood', 'Markham', 'Marshall Park', 'Multnomah',
                      'South Burlingame', 'South Portland', 'Southwest Hills', 'West Portland Park']

validEndorsement = {"CT": 0, "ED": 0, "EX": 0, "TO": 0}
licenseType = ['MD', 'MR', 'MC', 'MW', 'MP', 'MU']
uniqueReceipts = {}
seen_mrl_nums = {}


def validate_suite_number(x):
    try:
        if (x[0] == '#' and x[1:].isdigit()) or (x[0] != '#' and x.isdigit()):
            return True
    except TypeError:
        pass
    return False


def validateMailingAddress(addr):
    return re.search(addressRegex, addr) is not None or \
           re.search(addressWithFacilityRegex, addr) is not None or \
           re.search(POBoxRegex, addr) is not None


def validateComplianceRegion(region):
    length = len(region)
    if length == 1:
        if region[0] in ['N', 'S', 'E', 'W']:
            return True
    if length == 2:
        if region[0] in ['N', 'S'] and region[1] in ['E', 'W']:
            return True
    return False


def validateEndorsement(endorsementList):
    # validates that each of the involved substrings are one of the endorse types and none are repeated.
    stringEndorsement = str(endorsementList).upper()
    if len(stringEndorsement) == 0 or stringEndorsement.lower() == 'nan':  # This is a valid outcome
        return True
    splitEndorse = stringEndorsement.split(',')
    for item in splitEndorse:
        if item in validEndorsement:
            validEndorsement[item] += 1
        else:
            return False
        if validEndorsement[item] > 1:
            return False
    return True


def validate_license_type(license):
    tempLicense = str(license)
    if len(license) > 2:
        if license[0:4] != 'DRE-':
            return False
        else:
            tempLicense = tempLicense[4:]
    if tempLicense in licenseType:
        return tempLicense
    else:
        return False


def validate_receipt_num(receiptNo):
    # validates parseable integer with no repeated values
    if receiptNo in uniqueReceipts or not str(receiptNo).isdigit():
        return False
    else:
        # Must be converted to string upon return! Otherwise casts to a float and refuses to be cast back
        uniqueReceipts[receiptNo] = 1
        return True


def validate_mrl_num(mrl):
    """
    Validate that this field matches "MRL<number>" pattern.
    """
    m = mrl.upper()
    if m[0:3] != "MRL" or not m[3:].isdigit() or m in seen_mrl_nums:
        return False
    seen_mrl_nums[m] = 1
    return True


def fmt_failed_row(row):
    msg = "Failed row: "
    for item in row:
        msg += f"{item}, "
    msg = msg[0:len(msg) - 2]
    return msg


def replacePhoneNumber(phone):
    return ''.join([d for d in phone if d.isdigit()])


def validatePhoneNumber(phone):
    return len(''.join([d for d in phone if d.isdigit()])) == 10


def validate_monetary_amount(amt):
    try:
        s = str(amt)
        if s.upper() == 'NAN':
            return True
        if s[0] == '$':
            s = s[1:]
        a = int(s)
        return a >= 0
    except ValueError:
        return False


def validate_data_file(df):
    def error_row(field_index, failed_row):
        msg = f"Invalid {df.columns[field_index]}.\n"
        msg += f"Failed element: {failed_row[field_index]}\n"
        msg += f"Failed row: {fmt_failed_row(failed_row)}"
        return False, msg

    df.rename(columns={'Unnamed: 0': 'row'}, inplace=True)

    for row in df.itertuples(index=False):
        # Submission Date: parseable into a datetime
        try:
            pd.to_datetime(row[RowNames.SUBMISSION_DATE.value], format='%m/%d/%y', errors="raise")
        except ValueError:
            return error_row(RowNames.SUBMISSION_DATE.value, row)
        # Facility Address: matches regex
        if re.match(addressRegex, row[RowNames.FACILITY_ADDRESS.value]) is None:
            return error_row(RowNames.FACILITY_ADDRESS.value, row)
        # 'Facility Suite #': '#' + digits
        if validate_suite_number(row[RowNames.FACILITY_SUITE.value]) == np.nan:
            return error_row(RowNames.FACILITY_SUITE.value, row)
        # Facility Zip: 5-digit number
        try:
            bad_zip = not 0 <= int(row[RowNames.FACILITY_ZIP.value]) < 100000
        except ValueError:
            bad_zip = True
        if bad_zip:
            return error_row(RowNames.FACILITY_ZIP.value, row)
        # Mailing Address: matches regex
        if not validateMailingAddress(row[RowNames.MAILING_ADDRESS.value]):
            return error_row(RowNames.MAILING_ADDRESS.value, row)
        # MRL: matches "MRL<number>"
        mrl = row[RowNames.MRL.value].lstrip()
        if not (mrl[0:3].upper() == 'MRL' and mrl[3:].isdigit()):
            return error_row(RowNames.MRL.value, row)
        # Neighborhood Association: in approved list
        if not row[RowNames.NEIGHBORHOOD_ASSN.value] in validNeighborhoods:
            return error_row(RowNames.NEIGHBORHOOD_ASSN.value, row)
        # Compliance Region: cardinal direction
        if not validateComplianceRegion(row[RowNames.COMPLIANCE_REGION.value]):
            return error_row(RowNames.COMPLIANCE_REGION.value, row)
        # Primary Contact Name - no validation
        # Email - matches regex
        if not re.match(emailRegex, row[RowNames.EMAIL.value]):
            return error_row(RowNames.EMAIL.value, row)
        # Phone: coerceable into a 10-digit number
        if not validatePhoneNumber(row[RowNames.PHONE.value]):
            return error_row(RowNames.PHONE.value, row)
        # Endorsement: combination from approved list
        if not validateEndorsement(row[RowNames.ENDORSE_TYPE.value]):
            return error_row(RowNames.ENDORSE_TYPE.value, row)
        # License Type: matches expected values
        if not validate_license_type(row[RowNames.LICENSE_TYPE.value]):
            return error_row(RowNames.LICENSE_TYPE.value, row)
        # Repeat location: in approved list
        if not str(row[RowNames.REPEAT_LOCATION.value]).upper() in repeat_location_values:
            return error_row(RowNames.REPEAT_LOCATION.value, row)
        # App complete: in approved list
        if not str(row[RowNames.APP_COMPLETE.value]).upper() in app_complete_values:
            return error_row(RowNames.APP_COMPLETE.value, row)
        # Fee schedule: parseable date
        try:
            pd.to_datetime(row[RowNames.FEE_SCHEDULE.value], errors="raise")
        except:
            return error_row(RowNames.FEE_SCHEDULE.value, row)
        # Receipt num: numeric value with no repeats
        if not validate_receipt_num(row[RowNames.RECEIPT_NUM.value]):
            return error_row(RowNames.RECEIPT_NUM.value, row)
        # Cash amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[RowNames.CASH_AMT.value]):
            return error_row(RowNames.CASH_AMT.value, row)
        # Check amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[RowNames.CHECK_AMT.value]):
            return error_row(RowNames.CHECK_AMT.value, row)
        # Card amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[RowNames.CARD_AMT.value]):
            return error_row(RowNames.CARD_AMT.value, row)
        # Check No./Approval Code
        # No validation here, since it seems that they can be any combination of characters
        # MRL num: matches "MRL<number>" with no repeats
        if not validate_mrl_num(row[RowNames.MRL_NUM.value]):
            return error_row(RowNames.MRL_NUM.value, row)

    # Regularize the following values:
    # Suite number
    df['Facility Suite #'] = df['Facility Suite #'].str.lstrip()
    # MRL
    df['MRL'] = df['MRL'].str.lstrip()
    # Phone numbers
    df['Phone'] = df['Phone'].apply(replacePhoneNumber)
    # Repeat location
    df['Repeat location?'] = df['Repeat location?'].apply(lambda x: str(x).upper())
    # App complete
    df['App complete?'] = df['App complete?'].apply(lambda x: str(x).upper())

    return True, None

# TODO: add something that leverages the validation to return pass/fail and a summary of errors
# TODO: add support for single-row input, via PUT (need to convert to dataframe)
