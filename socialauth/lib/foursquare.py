from oauth import oauth
from django.conf import settings
import httplib

FOURSQUARE_AUTHENTICATION_URL = 'https://foursquare.com/oauth2/authenticate'
FOURSQUARE_ACCESS_TOKEN_URL = 'https://foursquare.com/oauth2/access_token'
FOURSQUARE_CONSUMER_KEY = getattr(settings, 'FOURSQUARE_CONSUMER_KEY')
FOURSQUARE_CONSUMER_SECRET = getattr(settings, 'FOURSQUARE_CONSUMER_SECRET')
REGISTERED_REDIRECT_URI = getattr(settings, 'FOURSQUARE_REGISTERED_REDIRECT_URI')

def get_http_connection():
    return httplib.HTTPSConnection('foursquare.com')

def get_response_body(oauth_request):
    http_conn = get_http_connection()
    http_conn.request('GET', oauth_request.to_url())
    response = http_conn.getresponse().read()
    return response
    

class FourSquareClient(object):
    def __init__(self):
        self.consumer = oauth.OAuthConsumer(FOURSQUARE_CONSUMER_KEY, FOURSQUARE_CONSUMER_SECRET)

    def get_authentication_url(self):
        parameters = {}
        parameters['client_id'] = FOURSQUARE_CONSUMER_KEY 
        parameters['response_type'] = 'code'
        parameters['redirect_uri'] = REGISTERED_REDIRECT_URI
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=FOURSQUARE_AUTHENTICATION_URL, parameters=parameters)
        return oauth_request.to_url()

    def get_access_token(self, foursquare_code):
        parameters = {}
        parameters['client_id'] = FOURSQUARE_CONSUMER_KEY
        parameters['client_secret'] = FOURSQUARE_CONSUMER_SECRET
        parameters['grant_type'] = 'authorization_code' 
        parameters['redirect_uri'] = REGISTERED_REDIRECT_URI
        parameters['code'] = foursquare_code
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=FOURSQUARE_ACCESS_TOKEN_URL, parameters=parameters)
        access_token_response = get_response_body(oauth_request) 
        return access_token_response
