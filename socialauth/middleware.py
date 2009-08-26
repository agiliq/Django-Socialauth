# FacebookConnectMiddleware.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

import md5
import urllib
import time
import simplejson
from datetime import datetime

# These values could be placed in Django's project settings
API_KEY = settings.FACEBOOK_API_KEY
API_SECRET = settings.FACEBOOK_API_SECRET

REST_SERVER = 'http://api.facebook.com/restserver.php'

# You can get your User ID here: http://developers.facebook.com/tools.php?api
MY_FACEBOOK_UID = '727912045'

NOT_FRIEND_ERROR = 'You must be my Facebook friend to log in.'
PROBLEM_ERROR = 'There was a problem. Try again later.'
ACCOUNT_DISABLED_ERROR = 'Your account is not active.'
ACCOUNT_PROBLEM_ERROR = 'There is a problem with your account.'

class FacebookConnectMiddleware(object):
    
    delete_fb_cookies = False
    facebook_user_is_authenticated = False
    
    def process_request(self, request):
        try:
             # Set the facebook message to empty. This message can be used to dispaly info from the middleware on a Web page.
            request.facebook_message = None

            # Don't bother trying FB Connect login if the user is already logged in
            if not request.user.is_authenticated():
            
                # FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
                if API_KEY in request.COOKIES:

                    signature_hash = self.get_facebook_signature(request.COOKIES, True)
                
                    # The hash of the values in the cookie to make sure they're not forged
                    if(signature_hash == request.COOKIES[API_KEY]):
                
                        # If session hasn't expired
                        if(datetime.fromtimestamp(float(request.COOKIES[API_KEY+'_expires'])) > datetime.now()):

                            # Make a request to FB REST(like) API to see if current user is my friend
                            are_friends_params = {
                                'method':'Friends.areFriends',
                                'api_key': API_KEY,
                                'session_key': request.COOKIES[API_KEY + '_session_key'],
                                'call_id': time.time(),
                                'v': '1.0',
                                'uids1': MY_FACEBOOK_UID,
                                'uids2': request.COOKIES[API_KEY + '_user'],
                                'format': 'json',
                            }
                            
                            
                            are_friends_hash = self.get_facebook_signature(are_friends_params)
    
                            are_friends_params['sig'] = are_friends_hash
                
                            are_friends_params = urllib.urlencode(are_friends_params)
                
                            are_friends_response  = simplejson.load(urllib.urlopen(REST_SERVER, are_friends_params))
                            
                            
                        
                            # If we are friends
                            if(are_friends_response[0]['are_friends'] is True):
                    
                                try:
                                    # Try to get Django account corresponding to friend
                                    # Authenticate then login (or display disabled error message)
                                    django_user = User.objects.get(username=request.COOKIES[API_KEY + '_user'])
                                    user = authenticate(username=request.COOKIES[API_KEY + '_user'], 
                                                        password=md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                    if user is not None:
                                        if user.is_active:
                                            login(request, user)
                                            self.facebook_user_is_authenticated = True
                                        else:
                                            request.facebook_message = ACCOUNT_DISABLED_ERROR
                                            self.delete_fb_cookies = True
                                    else:
                                       request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                       self.delete_fb_cookies = True
                                except User.DoesNotExist:
                                    # There is no Django account for this Facebook user.
                                    # Create one, then log the user in.
                    
                                    # Make request to FB API to get user's first and last name
                                    user_info_params = {
                                        'method': 'Users.getInfo',
                                        'api_key': API_KEY,
                                        'call_id': time.time(),
                                        'v': '1.0',
                                        'uids': request.COOKIES[API_KEY + '_user'],
                                        'fields': 'first_name,last_name',
                                        'format': 'json',
                                    }

                                    user_info_hash = self.get_facebook_signature(user_info_params)

                                    user_info_params['sig'] = user_info_hash
                    
                                    user_info_params = urllib.urlencode(user_info_params)

                                    user_info_response  = simplejson.load(urllib.urlopen(REST_SERVER, user_info_params))
                    
                    
                                    # Create user
                                    user = User.objects.create_user(request.COOKIES[API_KEY + '_user'], '', 
                                                                    md5.new(request.COOKIES[API_KEY + '_user'] + 
                                                                    settings.SECRET_KEY).hexdigest())
                                    user.first_name = user_info_response[0]['first_name']
                                    user.last_name = user_info_response[0]['last_name']
                                    user.save()
                    
                                    # Authenticate and log in (or display disabled error message)
                                    user = authenticate(username=request.COOKIES[API_KEY + '_user'], 
                                                        password=md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                    if user is not None:
                                        if user.is_active:
                                            login(request, user)
                                            self.facebook_user_is_authenticated = True
                                        else:
                                            request.facebook_message = ACCOUNT_DISABLED_ERROR
                                            self.delete_fb_cookies = True
                                    else:
                                       request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                       self.delete_fb_cookies = True
                            # Not my FB friend
                            else:
                                request.facebook_message = NOT_FRIEND_ERROR
                                self.delete_fb_cookies = True
                            
                        # Cookie session expired
                        else:
                            logout(request)
                            self.delete_fb_cookies = True
                        
                   # Cookie values don't match hash
                    else:
                        logout(request)
                        self.delete_fb_cookies = True
                    
            # Logged in
            else:
                # If FB Connect user
                if API_KEY in request.COOKIES:
                    # IP hash cookie set
                    if 'fb_ip' in request.COOKIES:
                        
                        try:
                            real_ip = request.META['HTTP_X_FORWARDED_FOR']
                        except KeyError:
                            real_ip = request.META['REMOTE_ADDR']
                        
                        # If IP hash cookie is NOT correct
                        if request.COOKIES['fb_ip'] != md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest():
                             logout(request)
                             self.delete_fb_cookies = True
                    # FB Connect user without hash cookie set
                    else:
                        logout(request)
                        self.delete_fb_cookies = True
                        
        # Something else happened. Make sure user doesn't have site access until problem is fixed.
        except:
            request.facebook_message = PROBLEM_ERROR
            logout(request)
            self.delete_fb_cookies = True
        
    def process_response(self, request, response):        
        
        # Delete FB Connect cookies
        # FB Connect JavaScript may add them back, but this will ensure they're deleted if they should be
        if self.delete_fb_cookies is True:
            response.delete_cookie(API_KEY + '_user')
            response.delete_cookie(API_KEY + '_session_key')
            response.delete_cookie(API_KEY + '_expires')
            response.delete_cookie(API_KEY + '_ss')
            response.delete_cookie(API_KEY)
            response.delete_cookie('fbsetting_' + API_KEY)
    
        self.delete_fb_cookies = False
        
        if self.facebook_user_is_authenticated is True:
            try:
                real_ip = request.META['HTTP_X_FORWARDED_FOR']
            except KeyError:
                real_ip = request.META['REMOTE_ADDR']
            response.set_cookie('fb_ip', md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest())
        
        # process_response() must always return a HttpResponse
        return response
                                
    # Generates signatures for FB requests/cookies
    def get_facebook_signature(self, values_dict, is_cookie_check=False):
        signature_keys = []
        for key in sorted(values_dict.keys()):
            if (is_cookie_check and key.startswith(API_KEY + '_')):
                signature_keys.append(key)
            elif (is_cookie_check is False):
                signature_keys.append(key)

        if (is_cookie_check):
            signature_string = ''.join(['%s=%s' % (x.replace(API_KEY + '_',''), values_dict[x]) for x in signature_keys])
        else:
            signature_string = ''.join(['%s=%s' % (x, values_dict[x]) for x in signature_keys])
        signature_string = signature_string + API_SECRET

        return md5.new(signature_string).hexdigest()


'myproject.FacebookConnectMiddleware.FacebookConnectMiddleware',