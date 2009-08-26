from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import User

from socialauth.lib import oauthtwitter
from socialauth.models import UserAssociation, TwitterUserProfile, AuthMeta
from socialauth.lib.facebook import get_user_info, get_facebook_signature

from datetime import datetime
import random

class OpenIdBackend:
    def authenticate(self, openid_key):
        try:
            assoc = UserAssociation.objects.get(openid_key = openid_key)
            return assoc.user
        except UserAssociation.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None




TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')



class TwitterBackend:
    """TwitterBackend for authentication
    """
    def authenticate(self, access_token):
        '''authenticates the token by requesting user information from twitter
        '''
        twitter = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, access_token)
        try:
            userinfo = twitter.GetUserInfo()
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise

        screen_name = userinfo.screen_name
        
        try:
            user = User.objects.get(username = 'twitter_%s'%screen_name )
            return user
        except User.DoesNotExist:
            user = User(username = 'twitter_%s'%screen_name)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            user.first_name = userinfo.name
            user.email = '%s@twitteruser.%s.com'%(userinfo.screen_name, settings.SITE_NAME)
            user.save()
            userprofile = TwitterUserProfile(user = user)
            userprofile.access_token = access_token.key
            userprofile.url = userinfo.url
            userprofile.location = userinfo.location
            userprofile.description = userinfo.description
            userprofile.profile_image_url = userinfo.profile_image_url
            userprofile.save()
            auth_meta = AuthMeta(user=user, provider='Twitter').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
        
class FacebookBackend:
    
    def authenticate(self, username, cookies):
        API_KEY = settings.FACEBOOK_API_KEY
        API_SECRET = settings.FACEBOOK_API_SECRET   
        REST_SERVER = 'http://api.facebook.com/restserver.php'
        if API_KEY in cookies:
            signature_hash = get_facebook_signature(API_KEY, API_SECRET, cookies, True)                
            if(signature_hash == cookies[API_KEY]) and (datetime.fromtimestamp(float(cookies[API_KEY+'_expires'])) > datetime.now()):
                user_info_response  = get_user_info(API_KEY, API_SECRET, cookies)
                username_ = 'facebook_%s' % user_info_response[0]['first_name']
                if not username == username_:
                    return None
                try:
                    user = User.objects.get(username = username)
                    return user
                except User.DoesNotExist:
                    user_email = '%s@facebookuser.%s.com'%(user_info_response[0]['first_name'], settings.SITE_NAME)
                    user_pass = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(8)])
                    user = User.objects.create(username = username, email=user_email, password=user_pass)
                    user.first_name = user_info_response[0]['first_name']
                    user.last_name = user_info_response[0]['last_name']
                    auth_meta = AuthMeta(user=user, provider='Facebook').save()
                    return user
            else:
                return None
                    
                
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
