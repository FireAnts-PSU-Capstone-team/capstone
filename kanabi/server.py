from flask import Blueprint, jsonify, make_response, request, session
from flask_login import login_required
from flask_principal import Permission, RoleNeed, PermissionDenied
from pandas.io.json import json_normalize
import markdown, markdown.extensions.fenced_code

from werkzeug.security import generate_password_hash
from functools import wraps
from pandas import json_normalize

from .models.IntakeRow import IntakeRow
import kanabi.driver as driver
from .responses import make_gui_response
from .configure import db
from .model import User

UPLOAD_FOLDER = 'resources'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
json_header = {"Content-Type": "application/json"}
admin_only_tables = ['archive', 'txn_history']

main_bp = Blueprint('main_bp', __name__)

# TODO: review permissions expectations given that most users will be 'editor'

# Administrator permissions. The '@admin_permission.require()' decorator can be used on endpoints.
# Additionally, 'with admin_permission.require():' can be used inside function definitions for conditionality.
admin_permission = Permission(RoleNeed('admin'))

# Editor permissions. Implemented the same as admin_permission via decorator, etc.
edit_permission = Permission(RoleNeed('editor'))


# Custom decorator that enforces read-only permissions and leaves input arguments untouched.
# If user is not in read-only mode then it will execute the user's intended request.
def write_permission(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        msg = 'No Write-permissions. User is in read-only mode.'
        if 'read_only_mode' in session:
            return make_gui_response(json_header, 400, msg)
        else:
            return function(*args, **kwargs)

    return wrapper

  
# Custom decorator that catches any server errors and return an appropriate response that includes CORS headers
def error_catching(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            return make_gui_response(json_header, 500, 'Something went wrong with our server. Exception: ' + str(e))
    return wrapper


@main_bp.route("/", methods=['GET'])
def index():
    return make_gui_response(json_header, 200, 'Hello World')

  
# Admin tools endpoint. Uses decorators with flask principal to enforce role-related access
@main_bp.route("/admin")
@admin_permission.require(http_exception=403)
def admin_tools():
    return make_gui_response(json_header, 200, 'OK')


# Registers the first 'admin' account. Ignores all requests after 'admin' account has already been created.
@main_bp.route("/makeadmin")
def register_admin():
    user = User.query.filter_by(name='admin', is_admin=True).first()
    if user:
        msg = 'An admin account has already been registered.'
        return make_gui_response(json_header, 400, msg)
    return make_gui_response(json_header, 200, 'OK')

@main_bp.route("/usrhello")
@login_required
def usr_hello():
    return make_gui_response(json_header, 200, 'OK')

# Creates the 'admin' account in the database. Should be executed once and only once, immediately after project
#   is created. This creates an admin-level user named 'admin' who can be used to conduct user setup
@main_bp.route("/makeadmin", methods=['POST'])
def register_admin_post():
    user = User.query.filter_by(name='admin', is_admin=True).first()
    if user:
        msg = 'An admin account has already been created.'
        return make_gui_response(json_header, 400, msg)
    else:
        password = request.form.get('password')
        email = request.form.get('email')
        new_user = User(email=email, password=generate_password_hash(password, method='sha256'), name='admin',
                        is_admin=True, is_editor=True)
        db.session.add(new_user)
        db.session.commit()
        return make_gui_response(json_header, 200, 'OK')

# Places the user into read-only mode
@main_bp.route("/enablereadonly")
@login_required
def enable_read_only():
    session['read_only_mode'] = True
    return make_gui_response(json_header, 200, 'OK')


# Takes user out of read-only mode
@main_bp.route("/disablereadonly")
@login_required
def disable_read_only():
    session['read_only_mode'] = False
    return make_gui_response(json_header, 200, 'OK')


# Test to verify that the '@write_permission' decorator is enforcing read-only mode
@main_bp.route('/writetest')
@login_required
@write_permission
def test_read_only():
    return make_gui_response(json_header, 200, 'OK')


def allowed_file(filename):
    """
    Checks an input file for approved extensions.
    Args:
        filename (str): file to check
    Returns (bool): file approved

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route("/list", methods=["GET", "POST"])
def fetch_data():
    """
    Displays the contents of the table listed in the request.
    Usage:
        GET /list?table=<table_name> to retrieve entire table
        POST /list to process specific query
    Returns ({}): JSON object of table data
    """
    if request.method == 'POST':
        table = request.json.get('table')
        if table is None:
            return make_response(jsonify('Table name not supplied.'), 400)

        # if table is admin-only, require admin status
        if table in admin_only_tables and not session['is_admin']:
            return make_response(jsonify('User must be logged in as admin to access this resource'), 403)

        query, response, status = driver.filter_table(request.json)
        return make_response(jsonify(response), status)

    if request.method == 'GET':
        table_name = request.args.get('table')
        if table_name is None:
            return make_response(jsonify('Table name not supplied.'), 400)
        try:
            columns = request.args.get('column')
            if columns is not None:
                columns = str.split(columns.strip(), ' ')

            # if table is admin-only, require admin status
            if table_name in admin_only_tables and not session['is_admin']:
                return make_response(jsonify('User must be logged in as admin to access this resource'), 403)

            table_info_obj = driver.get_table(table_name, columns)
            return make_response(jsonify(table_info_obj), 200)
        except driver.InvalidTableException:
            return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


@main_bp.route("/load", methods=["PUT", "POST"])
@error_catching
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

            valid, error_msg = driver.validate_row(request.get_json(force=True))
            if not valid:
                result = {'failed_row': error_msg}
                return make_response(jsonify(result), 400)
            try:
                row_data = IntakeRow(request.get_json(force=True)).value_array()
            except (KeyError, ValueError):
                message = {'message': 'Error encountered while parsing input'}
                return make_response(jsonify(message), 400)

            row_count, fail_row = driver.insert_row(table_name, row_data)
            if row_count == 1:
                status = 200
                result = {
                    'message': 'PUT completed',
                    'rows_affected': row_count
                }
            elif row_count == -1:
                status = 400
                result = {
                    'message': 'PUT failed',
                    'cause': 'duplicate row number'
                }
            else:
                status = 400
                result = {
                    'message': 'PUT failed',
                    'fail_row': fail_row
                }
            return make_response(jsonify(result), status)

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
                    'message': 'File processed, but with failed rows:',
                    'result': result_obj
                }
                return make_response(jsonify(result), 400)

    result = {'message': 'Unsupported operation.'}
    return make_response(jsonify(result), 404)


@main_bp.route('/metadata', methods=['GET'])
def show_metadata():
    """
    Display the contents of the metadata table.
    Returns ({}): response object containing the contents of the table.
    """
    response_body = jsonify(driver.get_table('metadata', None))
    return make_response(response_body, 200)


@main_bp.route('/export', methods=['GET'])
def export_csv():
    """
    Returns CSV of the table listed in the request.
    Usage:
        GET /export?table=<table_name> -o outputfile.csv to retrieve CSV of table
    Returns ({}): CSV object of table data
    """
    if request.method == 'GET':
        table_name = request.args.get('table')
        if table_name is None:
            return make_response(jsonify('Table name not supplied.'), 400)
        try:
            table_output = driver.get_table(table_name, None)
            df = json_normalize(table_output)
            table_info_obj = df.to_csv(index=False)
            return make_response(table_info_obj, 200)
        except driver.InvalidTableException:
            return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


@main_bp.route("/delete", methods=["GET"])
def delete_row():
    """
    Delete a row of data from the specified table.
    Usage: /delete?table=<table_name>&row=<row_num>
    Returns ({}): Response object containing status message
    """
    table_name = request.args.get('table', '')
    row_nums = request.args.get('row', '')
    if table_name == '' or row_nums == '':
        return make_response(jsonify('Table name or row number not supplied.'), 400)
    try:
        row_nums = str.split(row_nums.strip(), ' ')
        table_info_obj = driver.delete_row(table_name, row_nums)
        return make_response(jsonify(table_info_obj), 200)
    except driver.InvalidTableException:
        return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)
    except driver.InvalidRowException:
        return make_response(jsonify('Row '.join(row_nums) + ' is invalid input.'), 404)


@main_bp.route('/update', methods=['POST'])
def update_table():
    """
    Update the contents of the intake table.
    Returns ({}): result of updating the contents of the table.
    """
    update_columns = {}
    row = None
    data_content_type = request.content_type

    if data_content_type is None:
        result = {'message': 'Update operation requires parameters.'}
        return make_response(jsonify(result), 400)

    if data_content_type.find('json') != -1:
        request_param = request.get_json(force=True)
    elif data_content_type.find('x-www-form-urlencoded') != -1:
        request_param = request.form
    else:
        result = {'message': f'Unsupported data content-type: {data_content_type}'}
        return make_response(jsonify(result), 400)

    for key in request_param:
        if key == 'row':
            row = request_param[key]
        else:
            update_columns[key] = request_param[key]

    if row is None:
        result = {'message': 'Row number must be specified.'}
        return make_response(jsonify(result), 400)

    try:
        row = int(row)
    except ValueError:
        result = {'message': 'Row must be a number.'}
        return make_response(jsonify(result), 400)

    if len(update_columns) == 0:
        result = {'message': 'No column provided to update.'}
        return make_response(jsonify(result), 400)

    # only update intake table now
    response_body = driver.update_table('intake', row, update_columns)
    result = {'message': response_body[1]}
    if response_body[0] == 0:
        # error on updating
        return make_response(jsonify(result), 400)
    else:
        # succeed on updating
        return make_response(jsonify(result), 200)


@main_bp.route('/restore', methods=['PUT'])
def restore_record():
    """
    Restore a record from the archive table to its original table
    Usage: /restore?row=<row_num>
    Returns ({}): result of restoring the contents to the table.
    """
    row_num = request.args.get('row', '')
    if row_num == '':
        return make_response(jsonify('Row number not supplied.'), 400)
    try:
        row_num = str.split(row_num.strip(), ' ')
        table_info_obj = driver.restore_row(row_num)
        return make_response(jsonify(table_info_obj), 200)
    except driver.InvalidRowException:
        return make_response(jsonify('Row '.join(row_num) + ' could not be restored automatically. '
                                                            'Contact your admin to have it restored'), 404)

@main_bp.route('/')
def landing_page():
    readme = open("./README.md", "r")
    md = markdown.markdown(
        readme.read(), extensions=["fenced_code"]
    )
    return md

@main_bp.route('/<path:path>', methods=["PUT", "POST", "GET"])
def catch_all(path):
    return make_response(jsonify('The requested endpoint does not exist.'), 404)
