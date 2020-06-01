from flask import Blueprint, request, current_app, session
from flask_login import login_user, login_required, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from werkzeug.security import generate_password_hash, check_password_hash
from .model import User
from .configure import db
from .responses import make_gui_response
from .driver import create_db_user
auth_bp = Blueprint('auth_bp', __name__)
json_header = {"Content-Type": "application/json"}

# Test Curls:
# curl -k https://localhost:443/signup -X POST -d "email=joseph@gmail.com&name=joseph&password=pwd"
# curl -k https://localhost:443/login -X POST -d "email=joseph@gmail.com&password=pwd" -c "test.cookie"
# curl -k https://localhost:443/logout -c test.cookie -b test.cookie


def fetch_user(email: str) -> User:
    return User.query.filter_by(email=email).first()


# Uses flask-login to log the user in and update their identity in flask-principal
@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = fetch_user(email)

    # Check if user actually exists and compare provided and stored password hashes
    if not user or not check_password_hash(user.password, password):
        # Reload page if user doesn't exist or the password was incorrect
        return make_gui_response(json_header, 400, 'Invalid Credentials')

    # Login-Manager creates new user session
    login_user(user, remember=remember)
    session['is_admin'] = user.is_admin

    # Tell Flask-Principal the identity has changed
    identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
    return make_gui_response(json_header, 200, 'OK')


# Adds the user to the database and rejects duplicate emails
@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # if a user is found, reject attempt
    if bool(fetch_user(email)):
        return make_gui_response(json_header, 400, 'A user with that email already exists')

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, password=generate_password_hash(password, method='sha256'),
                    name=name, is_admin=False, is_editor=False)
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    #add new user into the postgres database
    create_db_user(email, new_user.password, new_user.is_admin)
    return make_gui_response(json_header, 200, 'OK')


# Logs the user out in flask-login and updates the flask-principle identity to be anonymous
@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():

    # Login-Manager removes the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    # Tell Flask-Principal the user is now anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return make_gui_response(json_header, 200, 'OK')
