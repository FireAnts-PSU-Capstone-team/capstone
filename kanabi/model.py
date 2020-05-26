from flask_login import UserMixin
from .configure import db


# To access these properties for the current user, you can use current_user.PROPERTY
# UserMixin input allows flask-login's Login-Manager to interface with our User class
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean(), default=False)
    is_editor = db.Column(db.Boolean(), default=False)

