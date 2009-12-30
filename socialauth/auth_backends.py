from django.contrib.auth.models import User
from django.conf import settings

from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, AuthMeta
from socialauth.lib.facebook import get_user_info, get_facebook_signature

from datetime import datetime
import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_API_SECRET = getattr(settings, 'FACEBOOK_API_SECRET', '')
FACEBOOK_REST_SERVER = getattr(settings, 'FACEBOOK_REST_SERVER', 'http://api.facebook.com/restserver.php')

class OpenIdBackend:
    def authenticate(self, openid_key, request, provider):
        try:
            assoc = UserAssociation.objects.get(openid_key = openid_key)
            return assoc.user
        except UserAssociation.DoesNotExist:
            #fetch if openid provider provides any simple registration fields
            nickname = None
            email = None
            if request.openid and request.openid.sreg:
                email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                email = request.openid.ax.get('email')
                nickname = request.openid.ax.get('nickname')
            if nickname is None :
                nickname =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            if email is None :
                valid_username = False
                email =  '%s@%s.%s.com'%(nickname, provider, settings.SITE_NAME)
            else:
                valid_username = True
            name_count = User.objects.filter(username__startswith = nickname).count()
            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
                user = User.objects.create_user(username,email)
            else:
                user = User.objects.create_user(nickname,email)
            user.save()
    
            #create openid association
            assoc = UserAssociation()
            assoc.openid_key = openid_key
            assoc.user = user
            if email:
                assoc.email = email
            if nickname:
                assoc.nickname = nickname
            if valid_username:
                assoc.is_username_valid = True
            assoc.save()
            
            #Create AuthMeta
            auth_meta = AuthMeta(user = user, provider = provider)
            auth_meta.save()
            return user
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None

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
            user_profile = TwitterUserProfile.objects.get(screen_name = screen_name)
            user = user_profile.user
            return user
        except TwitterUserProfile.DoesNotExist:
            #Create new user
            same_name_count = User.objects.filter(username__startswith = screen_name).count()
            if same_name_count:
                username = '%s%s' % (screen_name, same_name_count + 1)
            else:
                username = screen_name
            user = User(username =  username)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            name_data = userinfo.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except:
                first_name, last_name =  screen_name, ''
            user.first_name, user.last_name = first_name, last_name
            user.email = '%s@twitteruser.%s.com'%(userinfo.screen_name, settings.SITE_NAME)
            user.save()
            userprofile = TwitterUserProfile(user = user, screen_name = screen_name)
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
    
    def authenticate(self, cookies):
        API_KEY = FACEBOOK_API_KEY
        API_SECRET = FACEBOOK_API_SECRET   
        REST_SERVER = FACEBOOK_REST_SERVER
        if API_KEY in cookies:
            signature_hash = get_facebook_signature(API_KEY, API_SECRET, cookies, True)                
            if(signature_hash == cookies[API_KEY]) and (datetime.fromtimestamp(float(cookies[API_KEY+'_expires'])) > datetime.now()):
                user_info_response  = get_user_info(API_KEY, API_SECRET, cookies)
                username = user_info_response[0]['first_name']
                try:
                    profile = FacebookUserProfile.objects.get(facebook_uid = str(user_info_response[0]['uid']))
                    return profile.user
                except FacebookUserProfile.DoesNotExist:
                    fb_data = user_info_response[0]
                    name_count = User.objects.filter(username__istartswith = username).count()
                    if name_count:
                        username = '%s%s' % (username, name_count + 1)
                    user_email = '%s@facebookuser.%s.com'%(user_info_response[0]['first_name'], settings.SITE_NAME)
                    user = User.objects.create(username = username, email=user_email)
                    user.first_name = fb_data['first_name']
                    user.last_name = fb_data['last_name']
                    user.save()
                    location = str(fb_data['current_location'])
                    fb_profile = FacebookUserProfile(facebook_uid = fb_data['uid'], user = user, profile_image_url = fb_data['pic_small'], location=location)
                    fb_profile.save()
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
