import pandas as pd
import numpy as np
import re as re

addressRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s(([a-zA-Z1-9]+\s)+)([a-zA-Z]+\.)'
addressWithFacilityRegex = r'^(\d+)\s([a-zA-Z]{1,2})\s(([a-zA-Z1-9]+\s)+)([a-zA-Z]+\.)\s(#\d+)'
POBoxRegex = r'([P|p][O|o])\s(Box|box)\s(\d+\,)((\s[a-zA-Z1-9]+)+)(\,\s[A-Z]{2}\s\d{5})'
    
validNeighbours = ['Central Northeast Neighbors', 'Beaumont-Wilshire', 'Cully', 'Grant Park', 'Hollywood', 'Madison South',
                        'Rose City Park', 'Roseway', 'Sumner', 'Sunderland', 'East Portland', 'Argay Terrace', 'Centennial', 
                        'Glenfair','Hazelwood','Lents','Mill Park','Parkrose Heights','Parkrose','Pleasant Valley',
                        'Powellhurst-Gilbert','Russell','Wilkes','Woodland Park', 'Northeast Coalition', 'Alameda',
                        'Boise', 'Concordia', 'Eliot','Humboldt','Irvington','King', 'Lloyd District', 'Sabin', "Sullivan's Gulch",
                        'Vernon', 'Woodlawn', 'Southeast Uplift','Ardenwald/Johnson Creek','Brentwood/Darlington','Brooklyn',
                        'Buckman','Creston-Kenilworth', 'Eastmoreland','Foster-Powell','Hosford-Abernethy','Kerns', 'Laurelhurst',
                        'Montavilla', 'Mt Scott-Arleta','Mt Tabor', 'North Tabor','Reed','Richmond','Sellwood-Moreland',
                        'South Tabor', 'Sunnyside','Woodstock','Arbor Lodge', 'Bridgeton', 'Cathedral Park', 'East Columbia',
                        'Hayden Island', 'Kenton', 'Overlook','Piedmont', 'Portsmouth', 'St Johns', 'University Park',
                        'Arlington Heights','Forest Park','Goosehollow Foothills','Hillside','Linnton','Northwest District',
                        'Northwest Heights','Old Town','Pearl District','Portland Downtown','Sylvan-Highlands','Southwest Neighborhoods Inc',
                        'Arnold Creek','Ashcreek','Bridlemile','Collins View','Crestwood','Far Southwest','Hayhurst','Healy Heights',
                        'Hillsdale','Homestead','Maplewood','Markham','Marshall Park','Multnomah','South Burlingame','South Portland',
                        'Southwest Hills','West Portland Park']

validEndorsment = {"CT": 0, "ED": 0, "EX":0, "TO":0}
licenseType = ['MD', 'MR', 'MC', 'MW', 'MP', 'MU']
uniqueReceipts = {}

def validateSuite_OR_fixAndValidateSuit_OR_RejectSuite(x):
    if x[0] == '#' and x[1:].isdigit():
        return x
    if x[0] != '#' and x.isdigit():
        return '#' + str(x)
    else:
        return np.nan

def validateMailingAddress(addr):
    if bool(re.search(addressRegex, addr)) == True:
        return addr
    elif bool(re.search(addressWithFacilityRegex, addr)) == True:
        return addr
    elif bool(re.search(POBoxRegex, addr)) == True:
        return addr
    else:
        return np.nan


def validateComplianceRegion(region):
    length = len(region)
    if length == 1:
        if region[0] == 'N' or region[0] == 'S' or region[0] == 'E' or region[0] == 'W':
            return region
        else:
            return np.nan
    if length == 2:
        if (region[0] == 'N' or region [0] == 'S') and (region[1] == 'E' or region[1] == 'W'):
            return region
        else: 
            return np.nan
        
    return np.nan


def validEndorsmentAndEndorsmentAmount(endorsmentList):
    stringEndorsment = str(endorsmentList).upper()
    if len(stringEndorsment) == 0: #This is a valid outcome
        return  stringEndorsment

    splitEndorse =  stringEndorsment.split(',')
    for item in splitEndorse:
        if item in validEndorsment:
            validEndorsment[item] += 1
        else:
            return np.nan

        if validEndorsment[item] > 1:
            return np.nan
    return stringEndorsment


def validateLicenseTypeAndPrefix(license):
    tempLicense = str(license)
    if len(license) > 2:
        if license[0:4] != 'DRE-':
            return np.nan
        else:
            tempLicense = tempLicense[4:]
        
    if tempLicense in licenseType:
        return tempLicense
    else:
        return np.nan


def validateIntegerAndUniqueness(receiptNo):
    if (receiptNo in uniqueReceipts) or str(receiptNo).isdigit() == False:
        return np.nan
    else:
        #Must be converted to string upon return! Otherwise casts to a float and refuses to be cast back
        uniqueReceipts[receiptNo] = 1
        return str(receiptNo)

def validateBeginInMRLEndsInIntegers(mrl):
        mrl.upper()
        if mrl[0:3] != "MRL":
            return np.nan
        if mrl[4:].isdigit() == False:
            return np.nan
        
        return mrl


def validate_data_file(df):
    #Dataframe is created with an "Unnamed column". The following cleans that up
    df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

    #Submission Date
    '''The following line takes the "Submission date" object and converts it to datetime, expecting it in the format of mm/dd/yy. 
    #If it encounters it out of that range, it fills in a "NaN", and attempts to determine if is a datetime expected in the format
    of mm/dd/yyyy. If yes, it converts that to a datetime object of format m/d/yy. If no 
    (such as out of bounds numbers, letters, etc), it fills in the value with NaN'''

    df['Submission date'] = pd.to_datetime(df['Submission date'], format='%m/%d/%y', errors="coerce").fillna(pd.to_datetime(df['Submission date'], format='%m/%d/%Y', errors="coerce")).dt.strftime('%m/%d/%y') 

    #Entity
    df['Entity'] = df['Entity'].str.title()

    #DBA
    df['DBA'] = df['DBA'].str.title()

    #Facility Address - validates format of street address through a regex (after adding a '.' just in case). Otherwise just rejects into NaN
    '''Regular expression translated: Any amount of integers but at least one, a space, a 1-2 letter word (for directions N, SW, etc)
    Followed by a space, followed by any number of letters/numbers (but at least one) followed by a space. 
    This is followed by a space, followed by a 1-4 letter word  (for the St., Ave., etc) followed by a period.
    This is difficult to maintain though!! Holy cow!'''

   
    df['Facility Address'] = df['Facility Address'].apply(lambda x: x if (x[-1] == '.') else x + '.')
    df['Facility Address'] = df['Facility Address'].where(df['Facility Address'].str.match(addressRegex))
    df['Facility Address'] = df['Facility Address'].str.title()
    print(df['Facility Address'])

    #Facility Suite Validation. Gets rid of white space in front. If it's just missing a #, adds it. Otherwise returns Nan
    #Function to use for the lambda later on
    df['Facility Suite #'] = df['Facility Suite #'].str.lstrip().apply(validateSuite_OR_fixAndValidateSuit_OR_RejectSuite)


    #Facility Zip - validate it has 5 numbers, otherwise Nan
    df['Facility Zip'] = df['Facility Zip'].apply(lambda x: x if (len(x) == 10) else np.nan)

    #Mailing Address Validation :/
    df['Mailing Address'] = df['Mailing Address'].apply(validateMailingAddress)


    #MRL Validation - validate that it beings with MRL and the last half is a number, otherwise nan
    df['MRL'] = df['MRL'].str.lstrip().apply(lambda x: x if (x[0:3] == 'MRL' and x[4:].isdigit()) else np.nan)

    #Neighborhood Association - validate that it's a part of this list. Probably best to input into text file to easily change in the future. Nan otherwise
    df['Neighborhood Association'] = df['Neighborhood Association'].apply(lambda x: x.title() if (str(x).title() in validNeighbours) else np.nan)

    #Compliance Region - ensures that the letters are in the right order, and that the correct letters exist. Otherwise nan
    df['Compliance Region'] = df['Compliance Region'].str.upper().apply(validateComplianceRegion)

    #Primary Contact Name (first) - just uppercases first letter, lowcases the rest
    df['Primary Contact Name (first)'] = df['Primary Contact Name (first)'].str.title()

    #Primary Contact Name (last) - just uppercases first letter, lowcases the rest
    df['Primary Contact Name (last)'] = df['Primary Contact Name (last)'].str.title()

    #Email - validate string format agains regular expression. NaN if it doesn't fit the format
    emailRegex = r'(\w+)\@(\w+)\.(\w+)'
    df['Email'] = df['Email'].where(df['Email'].str.match(emailRegex))

    #Phone = Replace the phone number formatting with only the raw numbers, and then ensure it's the correct length. Nan otherwise
    df['Phone'] = df['Phone'].apply(lambda x: ''.join([i for i in x if i.isdigit()]))
    df['Phone'] = df['Phone'].apply(lambda x: x if (len(x) == 10) else np.nan)

    #Endorse type - validates that each of the involved substrings are one of the endorse types and none are repeated. If not, NaN
    df['Endorse Type'] = df['Endorse Type'].apply(validEndorsmentAndEndorsmentAmount)

    #License Type - validates if appropriate license type (can have DRE in front). Otherwise NaN
    df['License Type'] = df['License Type'].apply(validateLicenseTypeAndPrefix)

        

    #Repeat location? - validate it's either a 'Y' or 'N' answer, and also upper cases it for good formatting
    df['Repeat location?'] = df['Repeat location?'].apply(lambda x: str(x).upper() if(str(x).upper() == 'Y' or str(x).upper() == 'N') else np.nan)

    #App complete?
    df['App complete?'] = df['App complete?'].apply(lambda x: str(x).upper())
    df['App complete?'] = df['App complete?'].apply(lambda x: x if (x == 'Y' or x == 'N' or x == 'YES' or x == 'NO' or x == 'N/A') else np.nan)

    #Fee Schedule - validates it's in a yyyy format. Otherwise yeets it out into a NaN
    df['Fee Schedule'] = pd.to_datetime(df['Fee Schedule'], format='%Y', errors="coerce").dt.strftime('%Y')

    #Receipt No. - validates that it's an integer, doesn't validate it's a unique number, Otherwise NaN
    #Ignoring the error because otherwise it doesn't convert NaN to an int, which is what we want
    df['Receipt No.'] = df['Receipt No.'].apply(validateIntegerAndUniqueness).astype(int, errors="ignore")

    #Cash Amount - validates it's a number and non-negative
    df['Cash Amount'] = df['Cash Amount'].apply(lambda x: x if (str(x)[1:].isdigit() and str(x)[1:] >= 0) else np.nan)

    #Check Amount - validates it's a number and non-negative
    df['Check Amount'] = df['Check Amount'].apply(lambda x: x if (str(x)[1:].isdigit() and str(x)[1:] >= 0) else np.nan)

    #Card Amount - validates it's a number and non-negative
    df['Card Amount'] = df['Card Amount'].apply(lambda x: x if (str(x)[1:].isdigit() and str(x)[1:] >= 0) else np.nan)

    #Check No./Approval Code
    #No validation here - since it seems that they can be any combo of letters, numbers, dashes, and we're assuming a non-malicious
    #user who wouldn't randomly put in in non-valid characters

    #MRL# - validates that it begins in "MRL" and ends in some number
    

    df['MRL#'] = df['MRL#'].apply(validateBeginInMRLEndsInIntegers)

    return df
