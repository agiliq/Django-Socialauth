import urllib
import urllib2
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import UserManager, User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
from django.utils.translation import ugettext as _
try:
    import json#Works with Python 2.6
except ImportError:
    from django.utils import simplejson as json

from socialauth.models import OpenidProfile, AuthMeta, FacebookUserProfile, TwitterUserProfile
from socialauth.forms import EditProfileForm
from socialauth import context_processors
from socialauth.lib.facebook import get_fb_data

"""
from socialauth.models import YahooContact, TwitterContact, FacebookContact,\
                            SocialProfile, GmailContact
"""

from openid_consumer.views import begin
from socialauth.lib import oauthtwitter
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
    return render_to_response('socialauth/login_page.html', context_processors.socialauth(request), 
            RequestContext(request))

def twitter_login(request):
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    request_token = twitter.getRequestToken()
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.getAuthorizationURL(request_token)
    return HttpResponseRedirect(signin_url)

def twitter_login_done(request):
    request_token = request.session.get('request_token', None)
    
    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
        # Redirect the user to the login page,
        # So the user can click on the sign-in with twitter button
        # TODO: use error page with message and redirect
        return HttpResponse("We didn't redirect you to twitter...")
    
    token = oauth.OAuthToken.from_string(request_token)
    
    # If the token from session and token from twitter does not match
    #   means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['request_token']
        # TODO: use error page with message and redirect
        return HttpResponse("Something wrong! Tokens do not match...")
    
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, token)  
    access_token = twitter.getAccessToken() 
    
    request.session['access_token'] = access_token.to_string()
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, 
                access_token)  
    twitter_user = twitter.GetUserInfo()
    message = ''
    if request.user.is_authenticated():
        user = request.user
        user_profile, created = TwitterUserProfile.objects.get_or_create(screen_name = twitter_user.screen_name,
            defaults = dict(user=user, access_token=access_token, url=twitter_user.url, 
                            location=twitter_user.location, description=twitter_user.description,
                            profile_image_url=twitter_user.profile_image_url)
            )
        if not created:
                #TODO:add a mesaage to the user that the fb account is already associated 
                # with a diffrent user account
                message = _('Twitter account is already associated with this account')
        user = user_profile.user

    user = authenticate(twitter_user=twitter_user)
    # if user is authenticated then login user
    if user:
        return login_and_next(request, user, message=message)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    # authentication was successful, use is now logged in
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

def openid_login(request):
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
    return begin(request, user_url='http://yahoo.com/')

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
    if request.openid:
        #check for already existing associations
        openid_key = str(request.openid)
        #authenticate and login
        user = authenticate(openid_key=openid_key, request=request, provider = provider)
        if user:
            return login_and_next(request, user)
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

def login_and_next(request, user, **params):
    login(request, user)
    if 'next' in request.session :
       next = request.session['next']
       del request.session['next']
       if len(next.strip()) >  0 :
           return HttpResponseRedirect(next)    
    url = '%s?%s' % (reverse(settings.EDIT_PROFILE_URLNAME), urllib.urlencode(params))
    return HttpResponseRedirect(url)

def facebook_login(request, device="mobile"):
    """
    This is a facebook login page for devices
    that cannot use the FBconnect javascript
    e.g. mobiles, iPhones
    """
    params = {}
    params["api_key"] = settings.FACEBOOK_API_KEY
    params["v"] = "1.0"
    params["next"] = reverse("socialauth_facebook_login_done")[1:] # remove leading slash
    params["canvas"] = "0"
    # Cancel link must be a full URL
    params["cancel"] = request.build_absolute_uri(reverse("socialauth_login_page")

    if device == "mobile":
        url = "http://m.facebook.com/tos.php?" + urrlib.urlencode(params)
    if device == "touch":
        url = "http://touch.facebook.com/tos.php?" + urllib.urlencode(params)
    else:
        # send them to the mobile site by default
        url = "http://m.facebook.com/tos.php?" + urllib.urlencode(params)
    return HttpResponseRedirect(url)

def facebook_login_done(request):
    message = ''
    API_KEY = settings.FACEBOOK_API_KEY
    if request.user.is_authenticated():
        fb_data = get_fb_data(API_KEY, settings.FACEBOOK_API_SECRET, request.COOKIES)
        if fb_data:
            user = request.user
            location = str(fb_data['current_location'])
            uid = str(fb_data['uid'])
            fb_profile, created = FacebookUserProfile.objects.get_or_create(facebook_uid = uid, 
                defaults=dict(user = user, profile_image_url = fb_data['pic_small'], location=location))
            # funny thing, we can keep old first and update last...
            if created:
                if not user.first_name:
                    user.first_name = fb_data['first_name']
                if not user.last_name:
                    user.last_name = fb_data['last_name']
                user.save()
            else:
                #TODO:add a mesaage to the user that the fb account is already associated 
                # with a diffrent user account
                message = _('Facebook account is already associated with this account')
    user = authenticate(cookies=request.COOKIES)
    if user:
        # if user is authenticated then login user
        return login_and_next(request, user, message=message)
    else:
        #Delete cookies and redirect to main Login page.
        del request.COOKIES[API_KEY + '_session_key']
        del request.COOKIES[API_KEY + '_user']
        # TODO: maybe the project has its own login page?
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    return HttpResponseRedirect(reverse('socialauth_login_page'))

def openid_login_page(request):
    return render_to_response('openid/index.html', {}, RequestContext(request))
    
def signin_complete(request):
    payload = {}
    return render_to_response('socialauth/signin_complete.html', payload, RequestContext(request))

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
            if user.openidprofile_set.all().count():
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
    
    if getattr(settings, 'LOGOUT_REDIRECT_URL', None):
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    else:
        return logout_response
