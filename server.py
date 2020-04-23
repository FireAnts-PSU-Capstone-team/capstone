from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS, cross_origin
import driver, os.path, re

app = Flask(__name__)


def load_domains_from_file():
    """
    Loads domain strings from file and parses the strings for wildcards. Strings containing wildcards are then
    converted into proper regex expressions and then placed into the origin list. This list is then used by CORS
    to allow for Cross-Domain Origin Requests for resources based on the various entries in that list.

    Each line of the 'accepted_domains.ini' file is converted into a regular expression.
    Lines beginning with a '#' are comments and are skipped. Empty lines are also skipped.
    Lines beginning with a '!' are raw regular expressions, and will be passed unmodified (minus the starting '!').

    Successful and unsuccessful CORS requests will still return a 200 OK response. The primary difference is that
    the successful responses will also contain the Access-Control-Allow-Methods, Access-Control-Allow-Headers,
    and Access-Control-Allow-Origin headers. It will not necessarily generate a failure message like browsers do.

    Simulate the cross-domain GET request using:
    $ curl -H "Origin: DOMAIN_NAME" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS --verbose \
        http://SERVER_IP_ADDRESS:PORTNUM/RESOURCE_PATH/RESOURCE_NAME

    Sample output on successful request
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: text/html; charset=utf-8
    < Allow: HEAD, GET, OPTIONS
    < Vary: Origin
    < Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
    < Access-Control-Allow-Headers: X-Requested-With
    < Access-Control-Allow-Origin: www.example.com
    < Content-Length: 0
    < Server: Werkzeug/1.0.1 Python/3.5.2
    < Date: Thu, 23 Apr 2020 05:19:17 GMT

    Sample output on unsuccessful request:
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: text/html; charset=utf-8
    < Allow: HEAD, GET, OPTIONS
    < Content-Length: 0
    < Server: Werkzeug/1.0.1 Python/3.5.2
    < Date: Thu, 23 Apr 2020 05:19:03 GMT
    """
    origin_list = []

    # Build the relative path to the file
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "accepted_domains.ini")

    # Populate the list of domains
    with open(path) as f:
        raw_list = f.read().splitlines()

    # Skip over comment lines and empty lines, and remove the '!' in front of raw regular expressions
    for line in raw_list:
        if not line:
            continue
        if (line[0] == '#'):
            continue
        if (line[0] == '!'):
            origin_list += [line[1:]]
            continue
    # Parse for special characters and insert the backspace escape character before each one
        line = re.sub(r'(?P<spchar>[^\w\s*.-])', r'\\\g<spchar>', line)
    # Generate a properly formatted regex string that utilizes wildcards and domain formatting
        line = re.sub(r'(?P<protocol>^.*)[.]?\*\.(?P<name>[\w]+$)', '^\g<protocol>.*\.\g<name>$', line.rstrip())
        origin_list += [line]
    return origin_list


# Load the list of accepted origin domains from the "accepted_domains.ini" file.
origin_list = load_domains_from_file()
# Including this header is requ#ired when using POST with JSONS across domains
app.config['CORS_HEADERS'] = 'Content-Type'
# Utilizes CORS with the list of origin strings and regex expressions to validate resource requests.
CORS(app, origins=origin_list)
status_ok = "{'status':'OK'}\n"


@app.route("/list", methods=["GET"])
def dump_table():
    """
    Displays the contents of the table listed in the request.
    Usage: /list?table=<table_name>
    Returns ({}): JSON object of table data
    """
    table_name = request.args.get('table', '')
    try:
        table_info_obj = driver.get_table(table_name)
        r = make_response(jsonify(table_info_obj), 200)
    except driver.InvalidTableException:
        r = make_response(jsonify('Table ' + table_name + ' does not exist.\n'))
    return r


# TODO: stub method
@app.route("/load", methods=["GET"])
def load_data():
    """
    Stub for a method to load data into one of the tables, e.g. via GUI
    Returns ({}): HTTP response
    """

    filename = 'files/Lists.xlsx'
    driver.process_file(filename)

    # response_obj = {'status': 'OK'}
    # response = jsonify(response_obj)
    return make_response(status_ok, 200)


# TODO: change this to a GET; any listed file must be in the files subdir and is consumed from there;
#  ensure this folder is copied to the container
@app.route("/file", methods=["GET", "POST"])
def upload_file(file_name):
    """
    Triggers the Python code to ingest a spreadsheet named <file_name> into the database.
    Usage: /file?file=</path/to/file.xlsx>
    Returns: HTTP response.
    """
    if request.method == 'POST':
        if file_name == '' or 'file' not in request.files:
            r = make_response('No file listed\n', 400)
        else:
            success = driver.process_file(file_name)
            if success:
                r = make_response('File processed successfully\n', 200)
            else:
                r = make_response('File could not be found\n', 400)
    else:
        r = make_response('Unsupported operation\n', 404)
    return r


@app.route('/metadata', methods=['GET'])
def show_metadata():
    """
    Display the contents of the metadata table.
    Returns: response object containing the contents of the table.
    """
    response_body = jsonify(driver.get_table('metadata'))
    return make_response(response_body, 200)


@app.route('/')
def hello_world():
    return make_response('Hello World\n', 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)