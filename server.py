from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS
import driver, sys
from cors import cors_setup
from models.IntakeRow import IntakeRow
from pandas import json_normalize
import collections

UPLOAD_FOLDER = 'resources'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
context = ('./configs/cert.pem', './configs/key.pem')
app = Flask(__name__)

# Load the list of accepted origin domains from the "accepted_domains.ini" file.
origin_list = cors_setup.load_domains_from_file()
# Including this header is required when using POST with JSON across domains
app.config['CORS_HEADERS'] = 'Content-Type'
# Utilizes CORS with the list of origin strings and regex expressions to validate resource requests.
CORS(app, origins=origin_list)


def allowed_file(filename):
    """
    Checks an input file for approved extensions.
    Args:
        filename (str): file to check
    Returns (bool): file approved

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/list", methods=["GET", "POST"])
def fetch_data():
    """
    Displays the contents of the table listed in the request.
    Usage:
        GET /list?table=<table_name> to retrieve entire table
        POST /list to process specific query
    Returns ({}): JSON object of table data
    """
    if request.method == 'POST':
        query, response, status = driver.filter_table(request.json)
        app.logger.info("Received query: " + query)
        return make_response(jsonify(response), status)

    if request.method == 'GET':
        table_name = request.args.get('table')
        if table_name is None:
            return make_response(jsonify('Table name not supplied.'), 400)
        try:
            # TODO: once authentication is in place, restrict the tables that can be listed here
            columns = request.args.get('column')
            if columns is not None:
                columns = str.split(columns.strip(), ' ')
            table_info_obj = driver.get_table(table_name, columns)
            return make_response(jsonify(table_info_obj), 200)
        except driver.InvalidTableException:
            return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


def validate_row(json_item):
    """
    Preps a JSON input row and passes it to the data validator. Returns the validator's response.
    Args:
        json_item ({}): input JSON
    Returns ((bool, str)): <whether row is valid>, <error message>
    """
    # If the incoming json object doesn't have a row associated with it, we add a temporary one for validation
    if 'row' not in json_item:
        json_item = collections.OrderedDict(json_item)
        json_item.update({'row': 999})
        json_item.move_to_end('row', last=False)
    df = json_normalize(json_item)
    return driver.validate_dataframe(df)


@app.route("/load", methods=["PUT", "POST"])
def load_data():
    """
    Load data into the database. PUT inserts a single row; POST uploads a file.
    Usage:
        PUT: /load?table=<table> -H "Content-Type: application/json" -d [<JSON object> | <filename>]
        POST: /load?file=</path/to/file.xlsx>
    Returns ({}): HTTPS response
    """
    if request.method == 'PUT':
        table_name = request.args.get('table')
        if table_name is None:
            result = {'message': 'Table name not specified.'}
            return make_response(jsonify(result), 400)
        else:
            try:
                driver.get_table(table_name, None)
            except driver.InvalidTableException:
                return make_response(jsonify(f"Table {table_name} does not exist."), 404)

            valid, error_msg = validate_row(request.get_json(force=True))
            if not valid:
                result = {'message': error_msg}
                return make_response(jsonify(result), 404)
            try:
                row_data = IntakeRow(request.get_json(force=True)).value_array()
            except (KeyError, ValueError) as err:
                message = {'message': err}
                return make_response(jsonify(message), 404)

            row_count, fail_row = driver.insert_row(table_name, row_data)
            if row_count == 1:
                result = {
                    'message': 'PUT completed',
                    'rows_affected': row_count
                }
            elif row_count == -1:
                result = {
                    'message': 'PUT failed',
                    'cause': 'duplicate row number'
                }
            else:
                result = {
                    'message': 'PUT failed',
                    'fail_row': fail_row
                }
            return make_response(jsonify(result), 200)

    elif request.method == 'POST':
        if 'file' not in request.files:
            result = {'message': 'No file listed'}
            return make_response(jsonify(result), 400)
        else:
            file = request.files['file']
            if not allowed_file(file.filename):
                result = {'message': f'Filename \"{file.filename}\" is not supported.'}
                return make_response(jsonify(result), 400)

            filename = f'{UPLOAD_FOLDER}/' + file.filename
            file.save(filename)
            success, result_obj = driver.process_file(filename)
            if success:
                result = {
                    'message': 'File processed successfully',
                    'result': result_obj
                }
                return make_response(jsonify(result), 200)
            else:
                if result_obj.get('status', '') == 'invalid':
                    return make_response(jsonify(result_obj.get('error_msg')), 400)
                result = {
                    'message': 'File processed, but with failed rows due to duplicate primary key:',
                    'result': result_obj
                }
                return make_response(jsonify(result), 400)

    result = {'message': 'Unsupported operation.'}
    return make_response(jsonify(result), 404)


@app.route('/metadata', methods=['GET'])
def show_metadata():
    """
    Display the contents of the metadata table.
    Returns ({}): response object containing the contents of the table.
    """
    response_body = jsonify(driver.get_table('metadata', None))
    return make_response(response_body, 200)


@app.route('/')
def hello_world():
    return make_response(jsonify('Hello World'), 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True, debug=True)
