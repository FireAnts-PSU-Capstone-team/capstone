from flask import Flask, request, jsonify
import driver

app = Flask(__name__)


@app.route("/list", methods=["GET"])
def dump_table():
    """
    Displays the contents of the table listed in the request.
    Usage: /list?table=<table_name>
    Returns ({}): JSON object of table data
    """
    table_name = request.args.get('table', '')
    table_info_obj = driver.get_table(table_name)
    return jsonify(table_info_obj)


@app.route("/load", methods=["GET"])
def load_data():
    """
    Stub for a method to load data into one of the tables, e.g. via GUI
    Returns ({}): HTTP response
    """

    filename = 'files/Lists.xlsx'
    driver.process_file(filename)

    response_obj = {'status': 'OK'}

    response = jsonify(response_obj)
    return response


@app.route("/file", methods=["POST"])
def upload_file():
    """
    POST <file> will trigger the Python code to ingest a spreadsheet into the database.
    Returns: HTTP response.
    """
    response = ''
    if request.method == 'POST':
        # right now, this is a dummy method, just illustrating that the response is returned
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '' or file.filename is None:
                return response
            else:
                driver.process_file(file)
                response_obj = {'status': 'OK'}
                response = jsonify(response_obj)
    return response


@app.route('/')
def index():
    return 'Hello World\n'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
