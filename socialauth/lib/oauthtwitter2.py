import httplib
import urllib2
import urllib
import time
import oauth.oauth as oauth
from twitter import User

from django.conf import settings
from django.utils import simplejson as json

CALLBACK_URL = 'http://example.com/newaccounts/login/done/'

TWITTER_URL = 'twitter.com'
REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'http://twitter.com/oauth/authorize'
TWITTER_CREDENTIALS_URL = 'https://twitter.com/account/verify_credentials.json'

#CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
#CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET

def connection():
    try:return connection._connection
    except AttributeError:
	   connection._connection = httplib.HTTPSConnection(TWITTER_URL)
	   return connection._connection

def oauth_response(req):
    connection().request(req.http_method, req.to_url())
    return connection().getresponse().read()

class TwitterOAuthClient(oauth.OAuthClient):
    def __init__(self, consumer_key, consumer_secret, request_token_url=REQUEST_TOKEN_URL, access_token_url=ACCESS_TOKEN_URL, authorization_url=AUTHORIZATION_URL):
        self.consumer_secret = consumer_secret
        self.consumer_key = consumer_key
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        
    def fetch_request_token(self, callback):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.request_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        return oauth.OAuthToken.from_string(oauth_response(oauth_request))
    
    def authorize_token_url(self, token, callback_url=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=self.authorization_url)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth_request.to_url()

    def fetch_access_token(self, token, verifier):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, verifier=verifier, http_url=self.access_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth.OAuthToken.from_string(oauth_response(oauth_request))

    def get_user_info(self, token):
        try:
	       oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=TWITTER_CREDENTIALS_URL)
	       oauth_request.sign_request(self.signature_method, self.consumer, token)
	       return User.NewFromJsonDict(json.loads(oauth_response(oauth_request)))
        except:
            pass
        return None
	
    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('POST', RESOURCE_URL, body=oauth_request.to_postdata(), headers=headers)
        response = self.connection.getresponse()
        return response.read()

def run_example():

    # setup
    print '** OAuth Python Library Example **'
    client = TwitterOAuthClient()
    
    pause()

    # get request token
    print '* Obtain a request token ...'
    pause()
    
    token = client.fetch_request_token()
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    pause()

    print '* Authorize the request token ...'
    pause()
    # this will actually occur only on some callback
    url = client.authorize_token_url(token)
    print 'GOT'
    print url
    pause()

    # get access token
    print '* Obtain an access token ...'
    pause()
    
    access_token = client.fetch_access_token(token)
    print 'GOT'
    print 'key: %s' % str(access_token.key)
    print 'secret: %s' % str(access_token.secret)
    pause()

    # access some protected resources
    print '* Access protected resources ...'
    pause()
    parameters = {'file': 'vacation.jpg', 'size': 'original', 'oauth_callback': CALLBACK_URL} # resource specific params
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='POST', http_url=RESOURCE_URL, parameters=parameters)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
    print 'REQUEST (via post body)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    params = client.access_resource(oauth_request)
    print 'GOT'
    print 'non-oauth parameters: %s' % params
    pause()

def pause():
    print ''
    time.sleep(1)

if __name__ == '__main__':
    run_example()
    print 'Done.'
