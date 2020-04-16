from flask import Flask, request, jsonify, make_response
import driver
from IntakeRow import IntakeRow

UPLOAD_FOLDER = 'files'
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
            return make_response('Table name not specified\n', 400)
        else:
            row_data = IntakeRow(request.get_json()).value_array()
            driver.insert_row(table_name, row_data)
            # TODO: find a way to make this return something meaningful
            # e.g., return 404 if table doesn't exist
            return make_response(jsonify('PUT complete'), 200)
    elif request.method == 'POST':
        if 'file' not in request.files or request.files.get('file', '') == '':
            return make_response(jsonify('No file listed'), 400)
        else:
            file = request.files['file']
            if not allowed_file(file.filename):
                return make_response(f'Filename \"{file.filename}\" is not supported.', 400)
            filename = f'{UPLOAD_FOLDER}/uploaded_' + file.filename
            file.save(filename)
            success = driver.process_file(filename)
            if success:
                return make_response(jsonify('File processed successfully'), 200)
            else:
                return make_response(jsonify('File could not be found'), 400)

    return make_response(jsonify('Unsupported operation'), 404)


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
