from flask import Flask, request, jsonify, Response, make_response
import driver

context = ('./cert.pem', './key.pem')
app = Flask(__name__)
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
@app.route("/file", methods=["POST"])
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
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True, debug=True)
