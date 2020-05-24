from configparser import ConfigParser

def loadSeqCounts(filename, tables, seqs):
# create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql

    if parser.has_section('row_sequences'):
        params = parser.items('row_sequences')
        for param in params:
            seqs[param[0]] = param[1]

