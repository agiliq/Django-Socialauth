from django.conf import settings 
from oauth.oauth import OAuthConsumer, OAuthRequest 
import httplib

GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET')
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'

def get_response_from_url(to_url):
    conn = httplib.HTTPSConnection('github.com')
    conn.request('GET', to_url)
    return conn.getresponse().read()

class GithubClient(object):
    def __init__(self):
        self.consumer = OAuthConsumer(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)

    def get_authorize_url(self):
        parameters = {'client_id':GITHUB_CLIENT_ID}
        oauth_request = OAuthRequest.from_consumer_and_token(self.consumer, http_url=GITHUB_AUTHORIZE_URL, parameters=parameters)
        return oauth_request.to_url()

    def get_access_token(self, code):
        parameters = {}
        parameters['client_id'] = GITHUB_CLIENT_ID
        parameters['client_secret'] = GITHUB_CLIENT_SECRET
        parameters['code'] = code
        oauth_request = OAuthRequest.from_consumer_and_token(self.consumer, http_url=GITHUB_ACCESS_TOKEN_URL, parameters=parameters)
        access_token = get_response_from_url(oauth_request.to_url())       
        return access_token
