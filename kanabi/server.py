from functools import wraps
from sqlite3 import DatabaseError

import markdown
import markdown.extensions.fenced_code
from flask import Blueprint, jsonify, make_response, request, session, Response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from pandas import json_normalize
from pandas.io.json import json_normalize
from werkzeug.security import generate_password_hash

import kanabi.driver as driver
from .auth import logout
from .configure import db
from .models.IntakeRow import IntakeRow
from .responses import make_gui_response
from .user import User

UPLOAD_FOLDER = 'kanabi/resources'
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


def allowed_file(filename):
    """
    Checks an input file for approved extensions.
    Args:
        filename (str): file to check
    Returns (bool): file approved
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_post_param():
    """
    Return a dict of param for POST request
    Returns (dict): param dict obj
    """
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

    return request_param


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


def user_admin(request: {}, mode: str) -> Response:
    """
    Handles user management, such as changing permissions levels or updating user information.
    Requires the user to be logged in as an admin.
    Args:
        request ({form}): the request object
        mode (str): the operation desired
    Returns (Response): status message

    """
    email = request.form.get('email')
    if email is None:
        return make_gui_response(json_header, 400, 'Target user email not provided')
    user = User.query.filter_by(email=email).one()
    if user is None:
        return make_gui_response(json_header, 400, 'Target user could not be found')

    if mode == 'makeadmin':
        user.is_admin = True
    elif mode == 'removeadmin':
        user.is_admin = False
    elif mode == 'makeeditor':
        user.is_editor = True
    elif mode == 'removeeditor':
        user.is_editor = False
    elif mode == 'changepassword':
        password = request.form.get('new_password')
        if password is None:
            return make_gui_response(json_header, 400, 'Password change request received, but password not provided')
        user.password = generate_password_hash(password, method='sha256')
    elif mode == 'changename':
        name = request.form.get('new_name')
        if name is None:
            return make_gui_response(json_header, 400, 'Name change request received, but name not provided')
        user.name = name
    elif mode == 'changeemail':
        email = request.form.get('new_email')
        if email is None:
            return make_gui_response(json_header, 400, 'Email change request received, but new email not provided')
        user.email = email
    elif mode == 'removeuser':
        db.session.delete(user)
        if user == current_user:
            db.session.commit()
            return logout()

    db.session.commit()
    return make_gui_response(json_header, 200, 'OK')


def list_users(mode: str) -> Response:
    """
    Allows a user with admin credentials to list active users and admins.
    Args:
        mode (str): selector for which list to retrieve
    Returns (Response): status and requested data

    """
    ret = {}
    if mode == 'listusers':
        users = User.query.all()
        for u in users:
            ret[u.id] = {
                'email': u.email,
                'name': u.name,
                'is_admin': u.is_admin
            }
    elif mode == 'listadmins':
        users = User.query.filter_by(is_admin=True)
        ret = {}
        for u in users:
            ret[u.id] = {
                'email': u.email,
                'name': u.name,
                'is_admin': u.is_admin
            }
    return make_response(ret, 200)


@main_bp.route("/admin/<mode>", methods=['GET', 'POST'])
def admin_tools(mode: str) -> Response:
    """
    Wrapper for admin-only tools.
    Args:
        mode (str): specifies the operation to be performed
    Returns (Response): containing status message/code and any requested data
    """
    user_admin_operations = ['makeadmin', 'removeadmin', 'makeeditor', 'removeeditor',
                             'changepassword', 'changename', 'changeemail', 'removeuser']
    if not session['is_admin']:
        return make_gui_response(json_header, 403, 'User must be logged in as admin to access this resource')
    else:
        if mode in user_admin_operations:
            if request.method == 'POST':
                return user_admin(request, mode)
            else:
                return make_gui_response(json_header, 400, 'This resource only supports POST method')
        elif mode in ['listusers', 'listadmins']:
            if request.method == 'GET':
                return list_users(mode)
            else:
                return make_gui_response(json_header, 400, 'This resource only supports GET method')
        else:
            return make_gui_response(json_header, 400, 'Unrecognized operation requested')


@main_bp.route("/edituser/<mode>", methods=['POST'])
@login_required
def edit_self_user(mode):
    """
    Allow a user to change some of their own settings.
    Returns (Response): status message
    """
    allowed_operations = ['changepassword', 'changename', 'changeemail', 'removeuser']
    email = request.form.get('email')
    user = User.query.filter_by(email=email).one()
    if current_user != user and not session['is_admin']:
        return make_gui_response(json_header, 403, 'Editing other users requires admin permissions')
    else:
        if mode not in allowed_operations:
            return make_gui_response(json_header, 400, 'Requested operation not available')
        else:
            return user_admin(request, mode)


# Simple litmus test that the user is logged in
@main_bp.route("/usrhello")
@login_required
def usr_hello():
    return make_gui_response(json_header, 200, 'OK')


@main_bp.route("/makeadmin", methods=['POST'])
def register_admin_post():
    """
    Creates the 'admin' account in the database. Should be executed once and only once, immediately after project
    is created. This creates an admin-level user named 'admin' who can be used to conduct user setup
    Though we're using a default username, we chose not to use 'admin' for some resistance to fuzzing attacks
    Returns (Response): status message
    """
    user = User.query.filter_by(is_admin=True).first()
    if user:
        msg = 'An admin account has already been created.'
        return make_gui_response(json_header, 400, msg)
    else:
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name', 'capstone_user_1')
        new_user = User(email=email, password=generate_password_hash(password, method='sha256'), name=name,
                        is_admin=True, is_editor=True)

        try:
            db.session.add(new_user)
            db.session.commit()
            # add new user into the postgres database with admin access
            driver.create_db_user(email, new_user.password, new_user.is_admin)
        except DatabaseError as e:
            return make_gui_response(json_header, 400, str(e))

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


@main_bp.route("/list", methods=["GET", "POST"])
@login_required
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

        query, response, status = driver.filter_table(request.json, current_user)
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

            table_info_obj = driver.get_table(table_name, columns, current_user)
            return make_response(jsonify(table_info_obj), 200)
        except driver.InvalidTableException:
            return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


@main_bp.route("/load", methods=["PUT", "POST"])
@login_required
@error_catching
def load_data():
    """
    Load data into the database. PUT inserts a single row; POST uploads a file.
    Usage:
        PUT: /load?table=<table> -H "Content-Type: application/json" -d [<JSON object> | <filename>]
        POST: /load?file=</path/to/file.xlsx>
    Returns ({}): HTTPS response
    """
    table_name = request.args.get('table')
    if table_name is None:
        result = {'message': 'Table name not specified.'}
        return make_response(jsonify(result), 400)

    if request.method == 'PUT':
        try:
            driver.get_table(table_name, None, current_user)
        except driver.InvalidTableException:
            return make_response(jsonify(f"Table {table_name} does not exist."), 404)

        valid, error_msg = driver.validate_row(request.get_json(force=True), table_name)
        if not valid:
            result = {'failed_row': error_msg}
            return make_response(jsonify(result), 400)
        try:
            if table_name.lower() == 'intake':
                from .models import IntakeRow
                row_data = IntakeRow.IntakeRow(request.get_json(force=True)).value_array()
            # further tables require implementation and validation
            # elif table_name.lower() == 'reports':
            #     from .models import ReportsRow
            #     row_data = ReportsRow.ReportsRow(request.get_json(force=True)).value_array()
            # elif table_name.lower() == 'violations':
            #     from .models import ViolationsRow
            #     row_data = ViolationsRow.ViolationsRow(request.get_json(force=True)).value_array()
            else:
                return make_response(jsonify(f"Table {table_name} is not supported for upload."), 400)
        except (KeyError, ValueError):
            message = {'message': 'Error encountered while parsing input'}
            return make_response(jsonify(message), 400)

        success, fail_row = driver.insert_row(table_name, row_data, current_user)
        if success:
            status = 200
            result = {
                'message': 'PUT completed'
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
            success, result_obj = driver.process_file(table_name, filename, current_user)
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
@login_required
def show_metadata():
    """
    Display the contents of the metadata table.
    Returns ({}): response object containing the contents of the table.
    """
    response_body = jsonify(driver.get_table('metadata', None, current_user))
    return make_response(response_body, 200)


@main_bp.route('/export', methods=['GET'])
@login_required
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
            table_output = driver.get_table(table_name, None, current_user)
            if isinstance(table_output,str):
                return make_response(jsonify(table_output),400)
            df = json_normalize(table_output)
            table_info_obj = df.to_csv(index=False)
            return make_response(table_info_obj, 200)
        except driver.InvalidTableException:
            return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)


@main_bp.route("/delete", methods=["GET"])
@login_required
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
        table_info_obj = driver.delete_row(table_name, row_nums, current_user)
        return make_response(jsonify(table_info_obj), 200)
    except driver.InvalidTableException:
        return make_response(jsonify('Table ' + table_name + ' does not exist.'), 404)
    except driver.InvalidRowException:
        return make_response(jsonify('Row '.join(row_nums) + ' is invalid input.'), 400)


@main_bp.route('/update', methods=['POST'])
@login_required
def update_table():
    """
    Update the contents of the intake table.
    Returns ({}): result of updating the contents of the table.
    """
    update_columns = {}
    row = None
    request_param = get_post_param()

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
    response_body = driver.update_table('intake', row, update_columns, current_user)
    result = {'message': response_body[1]}
    if response_body[0] == 0:
        # error on updating
        return make_response(jsonify(result), 400)
    else:
        # succeed on updating
        return make_response(jsonify(result), 200)


@main_bp.route('/restore', methods=['PUT'])
@login_required
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
        table_info_obj = driver.restore_row(row_num, current_user)
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
