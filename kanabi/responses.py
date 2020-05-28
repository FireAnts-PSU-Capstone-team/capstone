from flask import make_response, jsonify, session
from flask_login import current_user, AnonymousUserMixin
from .cors import cors_setup

origin_list = []


# Makes a response formatted for use with the frontend GUI
def make_gui_response(headers, return_code, status_msg):
    '''
    Proper responses that pass CORS should contain the following headers:
    Access-Control-Allow-Headers = Authorize  (used in browser's pre-flight request)
    Access-Control-Allow-Origin = FULLY_QUALIFIED_DOMAIN_NAME (must match Origin header)
    Access-Control-Allow-Credentials = True  (required if cookies are used for login)

    Test Curls:
    $ curl -k -i -X OPTIONS -H "Origin: https://ALLOWED_DOMAIN_NAME" -H 'Access-Control-Request-Method: POST'
           -H 'Access-Control-Request-Headers: Content-Type, Authorization' "https://DOMAIN_NAME:PORT/ENDPOINT"

    Successful Response (Passes CORS):
    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, PUT, OPTIONS, POST
    Access-Control-Allow-Origin: https://kanabi-gui.herokuapp.com
    Access-Control-Allow-Headers: Authorization, Content-Type
    Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
    Vary: Origin, Cookie
    Set-Cookie: session=.eJyrVspMSc0rySyp1EssLcmIL6ksSFWyyivNydFByGSmQIRqAZu4EWc.Xs8_-g.HQTLJSSfqKETLQPPuceCn8sqG7o; HttpOnly; Path=/
    Content-Length: 0
    Server: Werkzeug/1.0.1 Python/3.6.10
    Date: Thu, 28 May 2020 04:37:14 GMT

    Failed Response (Doesn't pass CORS)
    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, PUT, OPTIONS, POST
    Vary: Cookie
    Set-Cookie: session=.eJyrVspMSc0rySyp1EssLcmIL6ksSFWyyivNydFByGSmQIRqAZu4EWc.Xs9Bxg.rM9DEBnYHgdKgrIcOTUNze1PMZc; HttpOnly; Path=/
    Content-Length: 0
    Server: Werkzeug/1.0.1 Python/3.6.10
    Date: Thu, 28 May 2020 04:44:54 GMT
    '''

    global origin_list
    if 'read_only_mode' not in session:
        session['read_only_mode'] = False

    if not isinstance(current_user._get_current_object(), AnonymousUserMixin):
        user_dict = {'name': current_user.name, 'email': current_user.email,
                     'read_only_mode': session['read_only_mode'], 'is_admin': current_user.is_admin}
    else:
        user_dict = {'logged_in': False}

    response_body = {'return_msg': status_msg, 'user': user_dict}
    response = make_response(jsonify(response_body), return_code)
    response.headers['Access-Control-Allow-Headers'] += ['Authorization']
    response.headers['Access-Control-Allow-Origin'] = origin_list
    response.headers['Access-Control-Allow-Credentials'] = True
    return response


def update_origin_list():
    global origin_list
    origin_list = cors_setup.load_domains_from_file()
    return origin_list
