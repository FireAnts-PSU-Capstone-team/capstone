"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_principal import Principal, RoleNeed, UserNeed, identity_loaded, Identity, AnonymousIdentity
from flask_cors import CORS
from kanabi.cors import cors_setup
from .responses import make_gui_response, update_origin_list, origin_list

db = SQLAlchemy()


# Creates the app and initializes core plugins and configurable parameters
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Loads default configuration from file and then overrides it with private instance-specific values
    # found in /instance/config.py
    app.config.from_pyfile('config.py')

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    # This can be accomplished using '$ export APP_CONFIG_FILE=/var/www/kanabi/config/production.py'
    # app.config.from_envvar('APP_CONFIG_FILE')

    # Initialize Plugins
    db.init_app(app)
    principals = Principal(app)
    login_manager = LoginManager()

    # Provides a custom response instead of automatically redirecting using login-required decorator
    @login_manager.unauthorized_handler
    def unauthorized():
        headers = {"Content-Type": "application/json"}
        return make_gui_response(headers, 400, 'Login Required')

    # Redirect users to login page if login is required to access endpoint. Endpoint is provided as an argument to be
    # redirected to after the user logs in again.
    login_manager.login_view = 'auth_bp.login'
    login_manager.init_app(app)

    # Set up CORS by loading the list of accepted origin domains from the "accepted_domains.ini" file.
    o_list = update_origin_list()

    # Including this header is required when using POST with JSON across domains
    app.config['CORS_HEADERS'] = 'Content-Type'
    # Utilizes CORS with the list of origin strings and regex expressions to validate resource requests.
    CORS(app, origins=o_list)

    # Uses flask-login to load user by their id. Receives an id, returns a user object.
    @login_manager.user_loader
    def load_user(user_id):
        # User ID is the primary key from the user table
        return User.query.get(int(user_id))

    # Upon loading user with Flask-Login assign an identity with flask-principal
    @principals.identity_loader
    def read_identity_from_flask_login():
        if current_user.is_authenticated:
            return Identity(current_user.id)
        return AnonymousIdentity()

    # Update user roles for editing or administrative capabilities with flask-principal
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if not isinstance(identity, AnonymousIdentity):
            identity.provides.add(UserNeed(identity.id))
            if current_user.is_editor:
                identity.provides.add(RoleNeed('editor'))
            if current_user.is_admin:
                identity.provides.add(RoleNeed('admin'))

    from .model import User

    with app.app_context():
        from kanabi import server
        from kanabi import auth

        for line in o_list:
            print('CORS: ACCEPTING REQUESTS FROM: {}'.format(line))

        # Apply CORS to Blueprints
        CORS(server.main_bp, origins=o_list)
        CORS(auth.auth_bp, origins=o_list)

        # Register Blueprints
        app.register_blueprint(server.main_bp)
        app.register_blueprint(auth.auth_bp)

        # Create Database Models
        db.create_all()
    return app
