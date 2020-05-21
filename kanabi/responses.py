from flask import make_response, jsonify, session
from flask_login import current_user, AnonymousUserMixin


# Makes a response formatted for use with the frontend GUI
def make_gui_response(headers, return_code, status_msg):
    if 'read_only_mode' not in session:
        session['read_only_mode'] = False

    if not isinstance(current_user._get_current_object(), AnonymousUserMixin):
        user_dict = {'name': current_user.name, 'email': current_user.email,
                     'read_only_mode': session['read_only_mode'], 'is_admin': current_user.is_admin}
    else:
        user_dict = {'name': '', 'email': '', 'read_only_mode': False, 'is_admin': False}

    response_body = {'headers': headers, 'returnCode': return_code, 'return_msg':status_msg, 'user': user_dict}
    return make_response(jsonify(response_body))
