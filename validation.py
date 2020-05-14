import pandas as pd
import numpy as np
import re as re
import json

from models.IntakeRow import ColNames

# addressRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s([a-zA-Z0-9\-\.]+\s)+([a-zA-Z]+)(\.?)'
# addressWithFacilityRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s(([a-zA-Z1-9]+\s)+)([a-zA-Z]+)(\.?)(\,?)\s(#\d+)'
# POBoxRegex = r'^([P|p][O|o])\s(Box|box|BOX)\s(\d)+(\,?)(\s)[a-zA-Z1-9]+(\,)*\s[A-Z]{2}(\,)*\s\d{5}'
emailRegex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
repeat_location_values = ['Y', 'N', 'X', 'NAN']
app_complete_values = ['M', 'N', 'N/A', 'Y', 'NAN']
valid_compliance_regions = ['N', 'NW', 'NE', 'W', 'SW', 'SE', 'NAN']

validNeighborhoods = ['Alameda', 'Arbor Lodge', 'Ardenwald/Johnson Creek', 'Argay Terrace', 'Arlington Heights',
                      'Arnold Creek', 'Ashcreek', 'Beaumont-Wilshire', 'Boise', 'Brentwood/Darlington', 'Bridgeton',
                      'Bridlemile', 'Brooklyn', 'Buckman', 'Cathedral Park', 'Centennial', 'Central Northeast Neighbors',
                      'Collins View', 'Concordia', 'Creston-Kenilworth', 'Crestwood', 'Cully', 'East Columbia',
                      'East Portland', 'Eastmoreland', 'Eliot', 'Far Southwest', 'Forest Park', 'Foster-Powell',
                      'Glenfair', 'Goosehollow Foothills', 'Grant Park', 'Hayden Island', 'Hayhurst', 'Hazelwood',
                      'Healy Heights', 'Hillsdale', 'Hillside', 'Hollywood', 'Homestead', 'Hosford-Abernethy',
                      'Humboldt', 'Irvington', 'Kenton', 'Kerns', 'King', 'Laurelhurst', 'Lents', 'Linnton',
                      'Lloyd District', 'Madison South', 'Maplewood', 'Markham', 'Marshall Park', 'Mill Park',
                      'Montavilla', 'Mt. Scott-Arleta', 'Mt Scott-Arleta', 'Mt. Tabor', 'Mt Tabor', 'Multnomah', 'N/A', 'North Tabor',
                      'Northeast Coalition', 'Northwest District', 'Northwest Heights', 'Old Town', 'Overlook',
                      'Parkrose', 'Parkrose Heights', 'Pearl District', 'Piedmont', 'Pleasant Valley',
                      'Portland Downtown', 'Portsmouth', 'Powellhurst-Gilbert', 'Reed', 'Richmond', 'Rose City Park',
                      'Roseway', 'Russell', 'Sabin', 'Sellwood-Moreland', 'South Burlingame', 'South Portland',
                      'South Tabor', 'Southeast Uplift', 'Southwest Hills', 'Southwest Neighborhood Inc', 'St. Johns', 'St Johns',
                      "Sullivan's Gulch", 'Sumner', 'Sunderland', 'Sunnyside', 'Sylvan-Highlands', 'University Park',
                      'Vernon', 'West Portland Park', 'Wilkes', 'Woodland Park', 'Woodlawn', 'Woodstock']

valid_endorsements = ["CT", "ED", "EX", "TO"]
license_types = ['MD', 'MR', 'MC', 'MW', 'MP', 'MU']
uniqueReceipts = {}
seen_mrls = {}
seen_mrl_nums = {}


# def validate_suite_number(x):
#     try:
#         if (x[0] == '#' and x[1:].isdigit()) or (x[0] != '#' and x.isdigit()):
#             return True
#     except TypeError:
#         pass
#     return False


# def validateMailingAddress(addr):
#     return re.search(addressRegex, addr) is not None or \
#            re.search(addressWithFacilityRegex, addr) is not None or \
#            re.search(POBoxRegex, addr) is not None


def validateEndorsement(endorsementList):
    # validates that each of the involved substrings are one of the endorse types and none are repeated.
    stringEndorsement = str(endorsementList).upper()
    if len(stringEndorsement) == 0 or stringEndorsement.lower() == 'nan':  # This is a valid outcome
        return True
    splitEndorse = stringEndorsement.split(',')
    # keep track of seen items
    endorsement_counts = {}
    for item in splitEndorse:
        # if we haven't seen the item before, set count to 0
        if item not in endorsement_counts:
            endorsement_counts[item] = 0
        # if item is valid, increment counter
        if item in valid_endorsements:
            endorsement_counts[item] += 1
        else:
            return False
        # if we've already seen the item, reject it
        if endorsement_counts[item] > 1:
            return False
    return True


def validate_license_type(lic):
    licenses = str(lic).split(',')
    for lic in licenses:
        if lic[:4] == 'DRE-':
            lic = lic[4:]
        if lic not in license_types:
            return False
    return True


def validate_receipt_num(receiptNo):
    # validates parseable integer with no repeated values
    if receiptNo in uniqueReceipts or not str(receiptNo).isdigit():
        return False
    else:
        # Must be converted to string upon return! Otherwise casts to a float and refuses to be cast back
        uniqueReceipts[receiptNo] = 1
        return True


# TODO: combine these 2 functions once we know how MRL and MRL# are related
def validate_mrl(mrl):
    """
    Validate that this field matches "MRL<number>" pattern and is unique for this field.
    """
    m = mrl.upper().split('-')[0]
    if m[0:3] != "MRL" or not m[3:].isdigit() or m in seen_mrls:
        return False
    seen_mrls[m] = 1
    return True


def validate_mrl_num(mrl):
    """
    Validate that this field matches "MRL<number>" pattern and is unique for this field.
    """
    m = mrl.upper().split('-')[0]
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
        if len(s) == 0 or s.upper() == 'NAN':
            return True
        if s[0] == '$':
            s = s[1:]
        a = int(s.replace(',', '').replace('.', ''))
        return a >= 0
    except ValueError:
        return False


def validate_dataframe(df):
    def error_row(field_index, failed_row):
        msg = {
            'invalid_column_name': df.columns[field_index],
            'failed_value': failed_row[field_index],
            'failed_row': fmt_failed_row(failed_row)
        }
        return False, json.dumps(msg)

    df.rename(columns={'Unnamed: 0': 'row'}, inplace=True)

    for row in df.itertuples(index=False):
        # Submission Date: parseable into a datetime
        try:
            pd.to_datetime(row[ColNames.SUBMISSION_DATE.value], format='%m/%d/%y', errors="raise")
        except ValueError:
            return error_row(ColNames.SUBMISSION_DATE.value, row)
        # Fields that shouldn't be null but aren't subject to other validation
        non_nulls = [ColNames.ENTITY, ColNames.FACILITY_ADDRESS, ColNames.MAILING_ADDRESS,
                     ColNames.FIRST_NAME, ColNames.LAST_NAME]
        for field in non_nulls:
            if row[field.value] == np.nan:
                return error_row(field.value, row)
        # Facility Zip: 5-digit number
        try:
            valid_zip = 0 <= int(row[ColNames.FACILITY_ZIP.value]) < 100000
        except ValueError:
            valid_zip = False
        if not valid_zip:
            return error_row(ColNames.FACILITY_ZIP.value, row)
        # MRL
        if not validate_mrl(row[ColNames.MRL.value]):
            return error_row(ColNames.MRL.value, row)
        # Neighborhood Association: in approved list
        if not row[ColNames.NEIGHBORHOOD_ASSN.value] in validNeighborhoods:
            _, err_row = error_row(ColNames.NEIGHBORHOOD_ASSN.value, row)
            e = json.loads(err_row)
            e['valid_neighborhoods'] = validNeighborhoods
            return False, json.dumps(e)
        # Compliance Region
        if not row[ColNames.COMPLIANCE_REGION.value] in valid_compliance_regions:
            return error_row(ColNames.COMPLIANCE_REGION.value, row)
        # Email - matches regex
        if not re.match(emailRegex, row[ColNames.EMAIL.value]):
            return error_row(ColNames.EMAIL.value, row)
        # Phone: coerceable into a 10-digit number
        if not validatePhoneNumber(row[ColNames.PHONE.value]):
            return error_row(ColNames.PHONE.value, row)
        # Endorsement: combination from approved list
        if not validateEndorsement(row[ColNames.ENDORSE_TYPE.value]):
            return error_row(ColNames.ENDORSE_TYPE.value, row)
        # License Type: matches expected values
        if not validate_license_type(row[ColNames.LICENSE_TYPE.value]):
            return error_row(ColNames.LICENSE_TYPE.value, row)
        # Repeat location: unique and in approved list
        if not str(row[ColNames.REPEAT_LOCATION.value]).upper() in repeat_location_values:
            return error_row(ColNames.REPEAT_LOCATION.value, row)
        # App complete: in approved list
        if not str(row[ColNames.APP_COMPLETE.value]).upper() in app_complete_values:
            return error_row(ColNames.APP_COMPLETE.value, row)
        # Fee schedule: parseable date
        try:
            pd.to_datetime(row[ColNames.FEE_SCHEDULE.value], errors="raise")
        except:
            return error_row(ColNames.FEE_SCHEDULE.value, row)
        # Receipt num: numeric value with no repeats
        if not validate_receipt_num(row[ColNames.RECEIPT_NUM.value]):
            return error_row(ColNames.RECEIPT_NUM.value, row)
        # Cash amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CASH_AMT.value]):
            return error_row(ColNames.CASH_AMT.value, row)
        # Check amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CHECK_AMT.value]):
            return error_row(ColNames.CHECK_AMT.value, row)
        # Card amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CARD_AMT.value]):
            return error_row(ColNames.CARD_AMT.value, row)
        # Check No./Approval Code: no validation
        # MRL num
        if not validate_mrl_num(row[ColNames.MRL_NUM.value]):
            return error_row(ColNames.MRL_NUM.value, row)

    # Regularize the following values:
    # Facility Address
    df['Facility Address'] = df['Facility Address'].str.title()
    # Mailing Address
    df['Mailing Address'] = df['Mailing Address'].str.title()
    # MRL
    df['MRL'] = df['MRL'].str.strip()
    # Phone numbers
    df['Phone'] = df['Phone'].apply(replacePhoneNumber)
    # Endorsement types
    df['Endorse Type'] = df['Endorse Type'].apply(lambda x: str(x).strip())
    # Repeat location
    df['Repeat location?'] = df['Repeat location?'].apply(lambda x: str(x).upper())
    # App complete
    df['App complete?'] = df['App complete?'].apply(lambda x: str(x).upper())

    return True, None
