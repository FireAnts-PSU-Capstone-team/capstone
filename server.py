from flask import Flask, request, jsonify, make_response
import driver
from models.IntakeRow import IntakeRow

UPLOAD_FOLDER = 'resources'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app = Flask(__name__)


def allowed_file(filename):
    """
    Checks an input file for approved extensions.
    Args:
        filename (str): file to check
    Returns (bool): file approved

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/list", methods=["GET"])
def dump_table():
    """
    Displays the contents of the table listed in the request.
    Usage: /list?table=<table_name>
    Returns ({}): JSON object of table data
    """
    table_name = request.args.get('table', '')
    if table_name == '':
        return make_response(jsonify('Table name not supplied.'), 400)
    try:
        table_info_obj = driver.get_table(table_name)
        return make_response(jsonify(table_info_obj), 200)
    except driver.InvalidTableException:
        return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


@app.route("/load", methods=["PUT", "POST"])
def load_data():
    """
    Load data into the database. PUT inserts a single row; POST uploads a file.
    Usage:
        PUT: /load?table=<table> -H "Content-Type: application/json" -d [<JSON object> | <filename>]
        POST: /load?file=</path/to/file.xlsx>
    Returns ({}): HTTP response
    """
    # TODO: add error handling if JSON schema doesn't match
    if request.method == 'PUT':
        table_name = request.args.get('table')
        if table_name is None:
            result = {'message': 'Table name not specified.'}
            return make_response(jsonify(result), 400)
        else:
            try:
                driver.get_table(table_name)
            except driver.InvalidTableException:
                return make_response(jsonify(f"Table {table_name} does not exist."), 404)
            row_data = IntakeRow(request.get_json()).value_array()
            (row_count, fail_row) = driver.insert_row(table_name, row_data)
            if row_count == 1:
                result = {
                    'message': 'PUT completed',
                    'rows_affected': row_count
                }
            else:
                result = {
                    'message': 'PUT failed',
                    'fail_row': fail_row
                }
            return make_response(jsonify(result), 200)
    elif request.method == 'POST':
        if 'file' not in request.files or request.files.get('file', '') == '':
            result = {'message': 'No file listed'}
            return make_response(jsonify(result), 400)
        else:
            file = request.files['file']
            if not allowed_file(file.filename):
                result = {'message': f'Filename \"{file.filename}\" is not supported.'}
                return make_response(jsonify(result), 400)

            filename = f'{UPLOAD_FOLDER}/uploaded_' + file.filename
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
                    return make_response(jsonify(result_obj.get('error_msg'), 400))
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
    response_body = jsonify(driver.get_table('metadata'))
    return make_response(response_body, 200)


@app.route('/')
def hello_world():
    return make_response(jsonify('Hello World'), 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
