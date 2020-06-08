# THIS IS A PRIVATE INSTANCE SPECIFIC CONFIG FILE. MODIFY THE VALUES AS APPROPRIATE
# THE VALUES IN THIS FILE WILL OVERRIDE THE DEFAULT VALUES IN '../config.py'


# Uncomment the line below and change the string to your secret key
SECRET_KEY = 'CHANGE_THIS_TO_YOUR_SECRET_KEY'

# Uncomment the following lines to customize the db URI or track-modification settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = True
DB_NAME = "kanabi_db_1"
DB_USERNAME = "kanabiadmin"
DB_PASSWORD = "password"

# Uncomment these flags for CSRF CORS spoofing protection, debugging, testing, etc.
# CSRF_ENABLED = True  # Protection against CORS origin spoofing
# DEBUG = True
# TESTING = False

# NOTE: In production leave out DEBUG and TESTING variables so the defaults are used
