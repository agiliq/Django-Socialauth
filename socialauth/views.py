import logging
import urllib
from oauth import oauth

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout

from socialauth.models import AuthMeta
from socialauth.forms import EditProfileForm

from openid_consumer.views import begin
from socialauth.lib import oauthtwitter2 as oauthtwitter
                            
from socialauth.lib.linkedin import *

LINKEDIN_CONSUMER_KEY = getattr(settings, 'LINKEDIN_CONSUMER_KEY', '')
LINKEDIN_CONSUMER_SECRET = getattr(settings, 'LINKEDIN_CONSUMER_SECRET', '')

ADD_LOGIN_REDIRECT_URL = getattr(settings, 'ADD_LOGIN_REDIRECT_URL', '')
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '')
LOGIN_URL = getattr(settings, 'LOGIN_URL', '')

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')

FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', '')


def del_dict_key(src_dict, key):
    if key in src_dict:
        del src_dict[key]

def login_page(request):
    return render_to_response('socialauth/login_page.html', {'next': request.GET.get('next', LOGIN_REDIRECT_URL)}, context_instance=RequestContext(request))

def linkedin_login(request):
    linkedin = LinkedIn(LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET)
    request_token = linkedin.getRequestToken(callback = request.build_absolute_uri(reverse('socialauth_linkedin_login_done')))
    request.session['linkedin_request_token'] = request_token
    signin_url = linkedin.getAuthorizeUrl(request_token)
    return HttpResponseRedirect(signin_url)

def linkedin_login_done(request):
    request_token = request.session.get('linkedin_request_token', None)

    # If there is no request_token for session
    # Means we didn't redirect user to linkedin
    if not request_token:
        # Send them to the login page
        return HttpResponseRedirect(reverse("socialauth_login_page"))
    try:
        linkedin = LinkedIn(settings.LINKEDIN_CONSUMER_KEY, settings.LINKEDIN_CONSUMER_SECRET)
        verifier = request.GET.get('oauth_verifier', None)
        access_token = linkedin.getAccessToken(request_token,verifier)

        request.session['access_token'] = access_token
        user = authenticate(linkedin_access_token=access_token)
    except:
        user = None

    # if user is authenticated then login user
    if user:
        login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del_dict_key(request.session, 'access_token')
        del_dict_key(request.session, 'request_token')
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    # authentication was successful, user is now logged in
    return HttpResponseRedirect(LOGIN_REDIRECT_URL)

def twitter_login(request):
    next = request.GET.get('next', None)
    if next:
        request.session['twitter_login_next'] = next
    
    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    request_token = twitter.fetch_request_token(callback = request.build_absolute_uri(reverse('socialauth_twitter_login_done')))
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.authorize_token_url(request_token)
    return HttpResponseRedirect(signin_url)

def twitter_login_done(request):
    request_token = request.session.get('request_token', None)
    verifier = request.GET.get('oauth_verifier', None)
    denied = request.GET.get('denied', None)
    
    # If we've been denied, put them back to the signin page
    # They probably meant to sign in with facebook >:D
    if denied:
        return HttpResponseRedirect(reverse("socialauth_login_page"))

    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
        # Redirect the user to the login page,
        return HttpResponseRedirect(reverse("socialauth_login_page"))

    token = oauth.OAuthToken.from_string(request_token)

    # If the token from session and token from twitter does not match
    # means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del_dict_key(request.session, 'request_token')
        # Redirect the user to the login page
        return HttpResponseRedirect(reverse("socialauth_login_page"))

    try:
        twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        access_token = twitter.fetch_access_token(token, verifier)

        request.session['access_token'] = access_token.to_string()
        user = authenticate(twitter_access_token=access_token)
    except:
        user = None
  
    # if user is authenticated then login user
    if user:
        login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del_dict_key(request.session, 'access_token')
        del_dict_key(request.session, 'request_token')
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    # authentication was successful, use is now logged in
    next = request.session.get('twitter_login_next', None)
    if next:
        del_dict_key(request.session, 'twitter_login_next')
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(LOGIN_REDIRECT_URL)

def openid_login(request):
    if 'openid_next' in request.GET:
        request.session['openid_next'] = request.GET.get('openid_next')
    if 'openid_identifier' in request.GET:
        user_url = request.GET.get('openid_identifier')
        request.session['openid_provider'] = user_url
        return begin(request, user_url = user_url)
    else:
        request.session['openid_provider'] = 'Openid'
        return begin(request)

def gmail_login(request):
    request.session['openid_provider'] = 'Google'
    return begin(request, user_url='https://www.google.com/accounts/o8/id')

def gmail_login_complete(request):
    pass


def yahoo_login(request):
    request.session['openid_provider'] = 'Yahoo'
    return begin(request, user_url='https://me.yahoo.com/')

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
    if hasattr(request,'openid') and request.openid:
        #check for already existing associations
        openid_key = str(request.openid)
	
        #authenticate and login
        try:
            user = authenticate(openid_key=openid_key, request=request, provider = provider)
        except:
            user = None
	    
        if user:
            login(request, user)
            if 'openid_next' in request.session :
                openid_next = request.session.get('openid_next')
                if len(openid_next.strip()) >  0 :
                    return HttpResponseRedirect(openid_next)
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
            # redirect_url = reverse('socialauth_editprofile')
            # return HttpResponseRedirect(redirect_url)
        else:
	        return HttpResponseRedirect(LOGIN_URL)
    else:
        return HttpResponseRedirect(LOGIN_URL)

def facebook_login(request):
    """
    Facebook login page
    """
    if request.REQUEST.get("device"):
        device = request.REQUEST.get("device")
    else:
        device = "user-agent"

    params = {}
    params["client_id"] = FACEBOOK_APP_ID
    params["redirect_uri"] = request.build_absolute_uri(reverse("socialauth_facebook_login_done"))

    url = "https://graph.facebook.com/oauth/authorize?"+urllib.urlencode(params)

    return HttpResponseRedirect(url)

def facebook_login_done(request):
    user = authenticate(request=request)

    if not user:
        request.COOKIES.pop(FACEBOOK_API_KEY + '_session_key', None)
        request.COOKIES.pop(FACEBOOK_API_KEY + '_user', None)

        # TODO: maybe the project has its own login page?
        logging.debug("SOCIALAUTH: Couldn't authenticate user with Django, redirecting to Login page")
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    login(request, user)
    
    logging.debug("SOCIALAUTH: Successfully logged in with Facebook!")
    
    if request.GET.get('next'):
        return HttpResponseRedirect(request.GET.get('next'))
    else:
        return HttpResponseRedirect(LOGIN_REDIRECT_URL)

def openid_login_page(request):
    return render_to_response('openid/index.html', context_instance=RequestContext(request))

@login_required
def signin_complete(request):
    return render_to_response('socialauth/signin_complete.html', context_instance=RequestContext(request))

@login_required
def editprofile(request):
    if request.method == 'POST':
        edit_form = EditProfileForm(user=request.user, data=request.POST)
        if edit_form.is_valid():
            user = edit_form.save()
            try:
                user.authmeta.is_profile_modified = True
                user.authmeta.save()
            except AuthMeta.DoesNotExist:
                pass
            if hasattr(user,'openidprofile_set') and user.openidprofile_set.count():
                openid_profile = user.openidprofile_set.all()[0]
                openid_profile.is_valid_username = True
                openid_profile.save()
            try:
                #If there is a profile. notify that we have set the username
                profile = user.get_profile()
                profile.is_valid_username = True
                profile.save()
            except:
                pass
            request.user.message_set.create(message='Your profile has been updated.')
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
    
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET.get('next'))
    elif getattr(settings, 'LOGOUT_REDIRECT_URL', None):
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    else:
        return logout_response

