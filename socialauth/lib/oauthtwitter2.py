import httplib
import time

import oauth.oauth as oauth
from twitter import User

from django.utils import simplejson as json

TWITTER_URL = 'twitter.com'
REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'http://twitter.com/oauth/authorize'
TWITTER_CREDENTIALS_URL = 'https://twitter.com/account/verify_credentials.json'


def get_connection():
    return httplib.HTTPSConnection(TWITTER_URL)


def oauth_response(req):
    connection = get_connection()
    connection.request(req.http_method, req.to_url())
    response = connection.getresponse().read()
    connection.close()
    return response


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
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            http_url=self.request_token_url,
            callback=callback
        )
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        return oauth.OAuthToken.from_string(oauth_response(oauth_request))

    def authorize_token_url(self, token, callback_url=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=token,
            http_url=self.authorization_url,
            callback=callback_url
        )
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth_request.to_url()

    def fetch_access_token(self, token, verifier):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=token,
            verifier=verifier,
            http_url=self.access_token_url
        )
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth.OAuthToken.from_string(oauth_response(oauth_request))

    def get_user_info(self, token):
        try:
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                self.consumer,
                token=token,
                http_url=TWITTER_CREDENTIALS_URL
            )
            oauth_request.sign_request(self.signature_method, self.consumer, token)
            return User.NewFromJsonDict(json.loads(oauth_response(oauth_request)))
        except:
            pass
        return None

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        connection = get_connection()
        body = oauth_request.to_postdata()
        connection.request('POST', RESOURCE_URL, body=body, headers=headers)
        response = connection.getresponse().read()
        connection.close()
        return response


def run_example():

    # setup
    print '** OAuth Python Library Example **'
    consumer_key = raw_input('Twitter Consumer Key:')
    consumer_secret = raw_input('Twitter Consumer Secret:')
    callback = 'http://example.com/newaccounts/login/done/'

    client = TwitterOAuthClient(consumer_key, consumer_secret)

    pause()

    # get request token
    print '* Obtain a request token ...'
    pause()

    token = client.fetch_request_token(callback)
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
    parameters = {
        'file': 'vacation.jpg',
        'size': 'original',
        'oauth_callback': callback,
    }  # resource specific params
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        client.consumer,
        token=token,
        http_method='POST',
        http_url=RESOURCE_URL,
        parameters=parameters
    )
    oauth_request.sign_request(client.signature_method, client.consumer, token)
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
