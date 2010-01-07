from django.contrib.auth.models import User
from django.conf import settings

from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, AuthMeta
from socialauth.lib.facebook import get_fb_data

from datetime import datetime
import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_API_SECRET = getattr(settings, 'FACEBOOK_API_SECRET', '')
FACEBOOK_REST_SERVER = getattr(settings, 'FACEBOOK_REST_SERVER', 'http://api.facebook.com/restserver.php')

def temp_email():
    return "%s@example.com" % User.objects.make_random_password(length=12)

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
            name_count = User.objects.filter(username__startswith = nickname).count()
            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
            else:
                username = nickname
            if email is None :
                valid_username = False
                email =  '%s@example.com'%nickname
            else:
                valid_username = True
            user = User.objects.create_user(username,email)
            user.is_active = False
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
    def authenticate(self, twitter_user):
        '''authenticates the token by requesting user information from twitter
        '''
        screen_name = twitter_user.screen_name
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
            name_data = twitter_user.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except:
                first_name, last_name =  '', ''
            user.first_name, user.last_name = first_name, last_name
            user.email = temp_email()
            user.is_active = False
            user.save()
            userprofile = TwitterUserProfile(user = user, screen_name = screen_name)
            # userprofile.access_token = access_token.key
            userprofile.url = twitter_user.url
            userprofile.location = twitter_user.location
            userprofile.description = twitter_user.description
            userprofile.profile_image_url = twitter_user.profile_image_url
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
        fb_data = get_fb_data(FACEBOOK_API_KEY, FACEBOOK_API_SECRET, cookies)
        if fb_data:
            username = fb_data['first_name']
            try:
                profile = FacebookUserProfile.objects.get(facebook_uid = str(fb_data['uid']))
                return profile.user
            except FacebookUserProfile.DoesNotExist:
                name_count = User.objects.filter(username__istartswith = username).count()
                if name_count:
                    username = '%s%s' % (username, name_count + 1)
                user_email = temp_email()
                user = User.objects.create(username = username, email=user_email)
                user.first_name = fb_data['first_name']
                user.last_name = fb_data['last_name']
                user.is_active = False
                user.save()
                location = str(fb_data['current_location'])
                fb_profile = FacebookUserProfile(facebook_uid = fb_data['uid'], user = user, profile_image_url = fb_data['pic_small'], location=location)
                fb_profile.save()
                auth_meta = AuthMeta(user=user, provider='Facebook').save()
                return user
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
