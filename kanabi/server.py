import collections

from flask import Blueprint, jsonify, make_response, request, render_template, redirect, url_for, flash, session, Response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from flask_cors import CORS
from kanabi.cors import cors_setup
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

main_bp = Blueprint('main_bp', __name__)

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
        headers = {"Content-Type": "application/json"}
        msg = 'No Write-permissions. User is in read-only mode.'
        if 'read_only_mode' not in session:
            return make_gui_response(headers, 400, msg)
        elif session['read_only_mode']:
            return make_gui_response(headers, 400, msg)
        else:
            return function(*args, **kwargs)
    return wrapper



# Homepage endpoint which loads the template for index.html
@main_bp.route("/", methods=['GET'])
def index():
        headers = {"Content-Type": "application/json"}
        return make_gui_response(headers, 200, 'OK')


# Profile endpoint which loads the profile and passes in read-only mode information
@main_bp.route('/profile')
@login_required
def profile():
    if 'read_only_mode' not in session:
        session['read_only_mode'] = False
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


# Admin tools endpoint. Uses decorators with flask principal to enforce role-related access
@main_bp.route("/admin")
@admin_permission.require(http_exception=403)
def admin_tools():
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


# Registers the first 'admin' account. Ignores all requests after 'admin' account has already been created.
@main_bp.route("/makeadmin")
def register_admin():
    user = User.query.filter_by(name='admin', is_admin=True).first()
    headers = {"Content-Type": "application/json"}
    if user:
        msg = 'An admin account has already been registered.'
        return make_gui_response(headers, 400, msg)
    return make_gui_response(headers, 200, 'OK')


@main_bp.route("/usrhello")
@login_required
def usr_hello():
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


# Actually creates the 'admin' account in the database using the submission form from makeadmin.html
@main_bp.route("/makeadmin", methods=['POST'])
def register_admin_post():
    user = User.query.filter_by(name='admin', is_admin=True).first()
    headers = {"Content-Type": "application/json"}
    if user:
        msg = 'An admin account has already been created.'
        return make_gui_response(headers, 400, msg)
    else:
        password = request.form.get('password')
        email = request.form.get('email')
        new_user = User(email=email, password=generate_password_hash('pass', method='sha256'), name='admin',
                        is_admin=True, is_editor=True)
        db.session.add(new_user)
        db.session.commit()
        headers = {"Content-Type": "application/json"}
        return make_gui_response(headers, 200, 'OK')


# Places the user into read-only mode
@main_bp.route("/enablereadonly")
@login_required
def enable_read_only():
    session['read_only_mode'] = True
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


# Takes user out of read-only mode
@main_bp.route("/disablereadonly")
@login_required
def disable_read_only():
    session['read_only_mode'] = False
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


# Test to verify that the '@write_permission' decorator is enforcing read-only mode
@main_bp.route('/writetest')
@login_required
@write_permission
def test_read_only():
    headers = {"Content-Type": "application/json"}
    return make_gui_response(headers, 200, 'OK')


def allowed_file(filename):
    """
    Checks an input file for approved extensions.
    Args:
        filename (str): file to check
    Returns (bool): file approved

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route("/list", methods=["GET"])
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
        # TODO: once authentication is in place, restrict the tables that can be listed here
        columns = request.args.get('column', '')
        if columns == '':
            columns = None
        else:
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


@main_bp.route("/load", methods=["PUT", "POST"])
def load_data():
    """
    Load data into the database. PUT inserts a single row; POST uploads a file.
    Usage:
        PUT: /load?table=<table> -H "Content-Type: application/json" -d [<JSON object> | <filename>]
        POST: /load?file=</path/to/file.xlsx>
    Returns ({}): HTTPS response
    """
    # TODO: add error handling if JSON schema doesn't match
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
                return make_response(jsonify(result),404)
            try:
                row_data = IntakeRow(request.get_json(force=True)).value_array()
            except (KeyError, ValueError) as err:
                message = {'message': err}
                return make_response(jsonify(message), 404)

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
        if 'file' not in request.files or request.files.get('file') is None:
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


@main_bp.route('/metadata', methods=['GET'])
def show_metadata():
    """
    Display the contents of the metadata table.
    Returns ({}): response object containing the contents of the table.
    """
    response_body = jsonify(driver.get_table('metadata', None))
    return make_response(response_body, 200)

