import httplib
import urllib2
import urllib
import time
import oauth.oauth as oauth

from django.conf import settings



REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
ACCESS_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'


class YahooOAuthClient(oauth.OAuthClient):

    def __init__(self, consumer_key, consumer_secret, request_token_url=REQUEST_TOKEN_URL, access_token_url=ACCESS_TOKEN_URL, authorization_url=AUTHORIZATION_URL):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def fetch_request_token(self, **kwargs):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.request_token_url, parameters=kwargs)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.request_token_url, data)
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())
    
    def authorize_token_url(self, token, callback_url=None):
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, callback=callback_url, http_url=self.authorization_url)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.authorization_url, data)
        return full_url
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, token, **kwargs):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=self.access_token_url, parameters = kwargs)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.access_token_url, data)
        response = urllib2.urlopen(full_url)
        return response
        #return oauth.OAuthToken.from_string(response.read())


    def access_resource(self, url, token, **kwargs):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=url, parameters = kwargs)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(url, data)
        response = urllib2.urlopen(full_url)
        return response

def run_example():

    # setup
    print '** OAuth Python Library Example **'
    client = GoogleOAuthClient(CONSUMER_KEY, CONSUMER_SECRET)
    pause()

    # get request token
    print '* Obtain a request token ...'
    pause()
    
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    token = client.fetch_request_token(oauth_request)
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    pause()

    print '* Authorize the request token ...'
    pause()
    
    print 'REQUEST (via url query string)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    # this will actually occur only on some callback
    url = client.authorize_token(oauth_request, get_url_only=True)
    print 'GOT'
    print url
    pause()

    # get access token
    print '* Obtain an access token ...'
    pause()
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    token = client.fetch_access_token(oauth_request)
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    pause()

    # access some protected resources
    print '* Access protected resources ...'
    pause()
    parameters = {'file': 'vacation.jpg', 'size': 'original', 'oauth_callback': CALLBACK_URL} # resource specific params
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