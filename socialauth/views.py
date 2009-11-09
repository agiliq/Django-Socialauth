from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import UserManager, User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
try:
    import json#Works with Python 2.6
except ImportError:
    from django.utils import simplejson as json

from socialauth.models import OpenidProfile, AuthMeta
from socialauth.forms import EditProfileForm

"""
from socialauth.models import YahooContact, TwitterContact, FacebookContact,\
                            SocialProfile, GmailContact
"""

from openid_consumer.views import begin
from socialauth.lib import oauthtwitter2 as oauthtwitter
from socialauth.lib import oauthyahoo
from socialauth.lib import oauthgoogle
from socialauth.lib.facebook import get_user_info, get_facebook_signature, \
                            get_friends, get_friends_via_fql

from oauth import oauth
from re import escape
import random
from datetime import datetime
from cgi import parse_qs



def login_page(request):
    payload = {'fb_api_key':settings.FACEBOOK_API_KEY,}
    return render_to_response('socialauth/login_page.html', payload, RequestContext(request))

def twitter_login(request):
    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    request_token = twitter.fetch_request_token()  
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.authorize_token_url(request_token)  
    return HttpResponseRedirect(signin_url)

def twitter_login_done(request):
    request_token = request.session.get('request_token', None)
    
    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
            # Redirect the user to the login page,
            # So the user can click on the sign-in with twitter button
            return HttpResponse("We didn't redirect you to twitter...")
    
    token = oauth.OAuthToken.from_string(request_token)
    
    # If the token from session and token from twitter does not match
    #   means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
            del request.session['request_token']
            # Redirect the user to the login page
            return HttpResponse("Something wrong! Tokens do not match...")
    
    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)  
    access_token = twitter.fetch_access_token(token)
    
    request.session['access_token'] = access_token.to_string()
    user = authenticate(access_token=access_token)
    
    # if user is authenticated then login user
    if user:
        login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    # authentication was successful, use is now logged in
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

def openid_login(request):
    request.session['openid_provider'] = 'Openid'
    return begin(request)

def gmail_login(request):
    request.session['openid_provider'] = 'Google'
    return begin(request, user_url='https://www.google.com/accounts/o8/id')

def gmail_login_complete(request):
    pass


def yahoo_login(request):
    request.session['openid_provider'] = 'Yahoo'
    return begin(request, user_url='http://yahoo.com')

def openid_done(request, provider=None):
    """
    When the request reaches here, the user has completed the Openid
    authentication flow. He has authorised us to login via Openid, so
    request.openid is populated.
    After coming here, we want to check if we are seeing this openid first time.
    If we are, we will create a new Django user for this Openid, else login the
    existing openid.
    """
    if not provider:
        provider = request.session.get('openid_provider', '')
    if  request.openid:
        #check for already existing associations
        openid_key = str(request.openid)
        #authenticate and login
        user = authenticate(openid_key=openid_key, request=request, provider = provider)
        if user:
            login(request, user)
        if 'openid_next' in request.session :
            openid_next = request.session.get('openid_next')
            if len(openid_next.strip()) >  0 :
                return HttpResponseRedirect(openid_next)    
        redirect_url = reverse('socialauth_signin_complete')
        return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)
    
def facebook_login_done(request):
    API_KEY = settings.FACEBOOK_API_KEY
    API_SECRET = settings.FACEBOOK_API_SECRET   
    REST_SERVER = 'http://api.facebook.com/restserver.php'
    # FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
    if API_KEY in request.COOKIES:
        signature_hash = get_facebook_signature(API_KEY, API_SECRET, request.COOKIES, True)                
        # The hash of the values in the cookie to make sure they're not forged
        # AND If session hasn't expired
        if(signature_hash == request.COOKIES[API_KEY]) and (datetime.fromtimestamp(float(request.COOKIES[API_KEY+'_expires'])) > datetime.now()):
            #Log the user in now.
            user = authenticate(cookies=request.COOKIES)
            if user:
                # if user is authenticated then login user
                login(request, user)
                return HttpResponseRedirect(reverse('socialauth_signin_complete'))
            else:
                #Delete cookies and redirect to main Login page.
                del request.COOKIES[API_KEY + '_session_key']
                del request.COOKIES[API_KEY + '_user']
                return HttpResponseRedirect(reverse('socialauth_login_page'))
    return HttpResponseRedirect(reverse('socialauth_login_page'))
            
    
def signin_complete(request):
    payload = {}
    return render_to_response('socialauth/signin_complete.html', payload, RequestContext(request))

@login_required
def editprofile(request):
    if request.method == 'POST':
        edit_form = EditProfileForm(user=request.user, data=request.POST)
        if edit_form.is_valid():
            user = edit_form.save()
            request.user.message_set.create('Your profile has been updated.')
            return HttpResponseRedirect('.')
    if request.method == 'GET':
        edit_form = EditProfileForm(user = request.user)
    payload = {'edit_form':edit_form}
    return render_to_response('socialauth/editprofile.html', payload, RequestContext(request))

def social_logout(request):
    # Todo
    # still need to handle FB cookies, session etc.
    
    # let the openid_consumer app handle openid-related cleanup
    from openid_consumer.views import signout as oid_signout
    oid_signout(request)
    
    # normal logout
    logout_response = logout(request)
    
    if settings.LOGOUT_REDIRECT_URL:
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    else:
        return logout_response
