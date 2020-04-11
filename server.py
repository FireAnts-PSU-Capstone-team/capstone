from flask import Flask, request, jsonify, Response, make_response
import driver, os

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app = Flask(__name__)
status_ok = "{'status':'OK'}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        r = make_response(jsonify('Table ' + table_name + ' does not exist.'))
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
@app.route("/file", methods=["POST"])
def upload_file():
    """
    Triggers the Python code to ingest a spreadsheet named <file_name> into the database.
    Usage: /file?file=</path/to/file.xlsx>
    Returns: HTTP response.
    """
    if request.method == 'POST':

        if 'file' not in request.files:
            return make_response('No file listed', 400)
        else:
            file = request.files['file']

            if file.filename == '' or file.filename is None:
                return make_response('No filename', 400)
            

            if not allowed_file(file.filename):
                return make_response(f'Filename \"{file.filename}\" is not supported.', 400)

            filename = f'{UPLOAD_FOLDER}/uploaded_' + file.filename
            file.save(filename)
            success = driver.process_file(filename)
            
            if success:
                return make_response('File processed successfully', 200)
            else:
                return make_response('File could not be found', 400)
    
    return make_response('Unsupported operation', 404)



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
    return make_response('Hello World', 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
