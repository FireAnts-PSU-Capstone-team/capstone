from datetime import datetime

import pandas as pd
import numpy as np
import re as re
import json

from models.IntakeRow import ColNames

# addressRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s([a-zA-Z0-9\-\.]+\s)+([a-zA-Z]+)(\.?)'
# addressWithFacilityRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s(([a-zA-Z1-9]+\s)+)([a-zA-Z]+)(\.?)(\,?)\s(#\d+)'
# POBoxRegex = r'^([P|p][O|o])\s(Box|box|BOX)\s(\d)+(\,?)(\s)[a-zA-Z1-9]+(\,)*\s[A-Z]{2}(\,)*\s\d{5}'
emailRegex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
valid_compliance_regions = ['N', 'NW', 'NE', 'W', 'SW', 'SE', 'NAN']

with open("resources/portland-neighborhoods.json","r") as f:
    validNeighborhoods = json.load(f)

valid_endorsements = ["CT", "ED", "EX", "TO"]
license_types = ['MD', 'MR', 'MC', 'MW', 'MP', 'MU']
seen_mrls = {}


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
    return str(receiptNo).isdigit()


def validate_mrl(mrl):
    """
    Validate that this field matches "MRL<number>" pattern and is unique for this field.
    """
    try:
        m = mrl.upper().split('-')[0]
        if m[0:3] != "MRL" or not m[3:].isdigit() or m in seen_mrls:
            return False
        seen_mrls[m] = 1
        return True
    except (ValueError, AttributeError):
        return False


def fmt_failed_row(row):
    msg = "Failed row: "
    for item in row:
        msg += f"{item}, "
    msg = msg[0:len(msg) - 2]
    return msg


def replacePhoneNumber(phone):
    try:
        return ''.join([d for d in phone if d.isdigit()])
    except TypeError:
        return phone


def validatePhoneNumber(phone):
    try:
        return len(''.join([d for d in phone if d.isdigit()])) == 10
    except (TypeError, AttributeError):
        if len(str(phone)) == 10:  # If no formatting/phone is passed in as an int
            return True
        else:
            return False


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

    i = 0
    msg = {}
    df[ColNames.VALIDATION_ERRORS.name] = df.apply(lambda x: '', axis=1)
    df.rename(columns={'Unnamed: 0': 'row'}, inplace=True)

    for row in df.itertuples(index=False):
        errorString = []
        # Submission Date: parseable into a datetime
        try:
            pd.to_datetime(row[ColNames.SUBMISSION_DATE.value], format='%m/%d/%y', errors="raise")
        except ValueError:
            errorString.append(ColNames.SUBMISSION_DATE.name)
        # Fields that shouldn't be null but aren't subject to other validation
        non_nulls = [ColNames.ENTITY, ColNames.FACILITY_ADDRESS, ColNames.MAILING_ADDRESS,
                     ColNames.PRIMARY_CONTACT_FIRST_NAME, ColNames.PRIMARY_CONTACT_LAST_NAME]
        for field in non_nulls:
            if row[field.value] == np.nan:
                errorString.append(field.name)
        # Facility Zip: 5-digit number
        try:
            valid_zip = 0 <= int(row[ColNames.FACILITY_ZIP.value]) < 100000
        except ValueError:
            valid_zip = False
        if not valid_zip:
            errorString.append(ColNames.FACILITY_ZIP.name)
        # MRL
        if not validate_mrl(row[ColNames.MRL.value]):
            errorString.append(ColNames.MRL.name)
        # Neighborhood Association: in approved list
        if not row[ColNames.NEIGHBORHOOD_ASSOCIATION.value] in validNeighborhoods:
            errorString.append(ColNames.NEIGHBORHOOD_ASSOCIATION.name)
        # Compliance Region
        if not row[ColNames.COMPLIANCE_REGION.value] in valid_compliance_regions:
            errorString.append(ColNames.COMPLIANCE_REGION.name)
        # Email - matches regex
        try:
            if not re.match(emailRegex, row[ColNames.EMAIL.value]):
                errorString.append(ColNames.EMAIL.name)
        except:  # any error, honestly
            errorString.append(ColNames.EMAIL.name)
        # Phone: coerceable into a 10-digit number
        if not validatePhoneNumber(row[ColNames.PHONE.value]):
            errorString.append(ColNames.PHONE.name)
        # Endorsement: combination from approved list
        if not validateEndorsement(row[ColNames.ENDORSE_TYPE.value]):
            errorString.append(ColNames.ENDORSE_TYPE.name)
        # License Type: matches expected values
        if not validate_license_type(row[ColNames.LICENSE_TYPE.value]):
            errorString.append(ColNames.LICENSE_TYPE.name)
        # Repeat location: not checked
        # App complete: not checked
        # Fee schedule: not checked
        # Receipt num: numeric value with no repeats
        if not validate_receipt_num(row[ColNames.RECEIPT_NUM.value]):
            errorString.append(ColNames.RECEIPT_NUM.name)
        # Cash amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CASH_AMOUNT.value]):
            errorString.append(ColNames.CASH_AMOUNT.name)
        # Check amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CHECK_AMOUNT.value]):
            errorString.append(ColNames.CHECK_AMOUNT.name)
        # Card amount: number, possibly preceded by '$'
        if not validate_monetary_amount(row[ColNames.CARD_AMOUNT.value]):
            errorString.append(ColNames.CARD_AMOUNT.name)
        # Check No./Approval Code: no validation
        # MRL num: not checked
        if len(errorString) != 0:
            error_cols = ','.join(str(x) for x in errorString)
            df.at[i, ColNames.VALIDATION_ERRORS.name] = error_cols
            msg[i] = error_cols
        i += 1

    # Regularize the following values:
    df['Submission date'] = df['Submission date'].apply(
        lambda x: x.strftime('%m/%d/%y') if isinstance(x, datetime) else x
    )
    # Facility Address
    df['Facility Address'] = df['Facility Address'].str.title()
    # Suite number
    df['Facility Suite #'] = df['Facility Suite #'].str.strip()
    # MRL
    df['MRL'] = df['MRL'].str.strip()
    # Phone numbers
    df['Phone'] = df['Phone'].apply(replacePhoneNumber)
    # Endorsement types
    df['Endorse Type'] = df['Endorse Type'].apply(lambda x: str(x).strip())

    # If dictionary is empty
    if not msg:
        return True, None

    return False, msg
