from configparser import ConfigParser

def loadseqcounts(filename, seqs):
# create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    if parser.has_section('row_sequences'):
        params = parser.items('row_sequences')
        for param in params:
            seqs[param[0]] = int(param[1])


def writeseqcounts(filename, seqs):
    parser = ConfigParser()
    parser['row_sequences']=seqs
    with open(filename, 'w') as configfile:
        parser.write(configfile)