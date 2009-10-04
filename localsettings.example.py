# Put your local settings here. This will override corresponding settings in settings.py.
# PLEASE DO NOT CHECK IN THIS FILE.

ADMINS = (
    ('Shabda', 'shabda@uswaretech.com'),
)


# This is for dev environment. Display debug messages.
DEBUG = True

# site ID
SITE_ID = 1

SITE_NAME = 'foobar'


DATABASE_ENGINE = 'sqlite3' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'data.db'              # Or path to database file if using sqlite3.
DATABASE_USER = ''               # Not used with sqlite3.
DATABASE_PASSWORD = ''      # Not used with sqlite3.
DATABASE_HOST = ''         # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                  # Set to empty string for default. Not used with sqlite3.

OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_SREG = {"requred": "nickname, email", "optional":"postcode, country", "policy_url": ""}

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''


FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''


AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )

LOGIN_REDIRECT_URL = '/login/done/'



