from flask import Flask, request, jsonify
import driver, os

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app = Flask(__name__)


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
    Usage: /file?file=</path/to/file.xlsx>
    Returns: HTTP response.
    """
    response_obj = {'status': 'Not work!'}
    if request.method == 'POST':
        # print(request.files)
        
        if 'file' in request.files:
            file = request.files['file']
            print('file: ')
            print(file)
            if file.filename == '' or file.filename is None:
                response_obj = {'status': 'Failed'}

            elif allowed_file(file.filename):
                filename = f'{UPLOAD_FOLDER}/uploaded_' + file.filename
                file.save(filename)
                driver.process_file(filename)
                response_obj = {'status': 'OK'}

    return jsonify(response_obj)


@app.route('/')
def index():
    return 'Hello World'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
