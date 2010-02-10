from django.contrib.auth.models import User
from django.conf import settings
from facebook import Facebook

from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, LinkedInUserProfile, AuthMeta
from socialauth.lib.facebook import get_user_info, get_facebook_signature
from socialauth.lib.linkedin import *

from datetime import datetime
import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')

# Harmonized with PyFacebook

FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', '')
FACEBOOK_URL = getattr(settings, 'FACEBOOK_URL', 'http://api.facebook.com/restserver.php')

# Linkedin

LINKEDIN_CONSUMER_KEY = getattr(settings, 'LINKEDIN_CONSUMER_KEY', '')
LINKEDIN_CONSUMER_SECRET = getattr(settings, 'LINKEDIN_CONSUMER_SECRET', '')

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
                email =  None #'%s@example.openid.com'%(nickname)
            else:
                valid_username = True
            name_count = User.objects.filter(username__startswith = nickname).count()
            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
                user = User.objects.create_user(username,email or '')
            else:
                user = User.objects.create_user(nickname,email or '')
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

class LinkedInBackend:
    """LinkedInBackend for authentication
    """
    def authenticate(self, linkedin_access_token):
        linkedin = LinkedIn(settings.LINKEDIN_CONSUMER_KEY, settings.LINKEDIN_CONSUMER_SECRET)
        # get their profile
        
        profile = ProfileApi(linkedin).getMyProfile(access_token = linkedin_access_token)

        try:
            user_profile = LinkedInUserProfile.objects.get(linkedin_uid = profile.id)
            user = user_profile.user
            return user
        except LinkedInUserProfile.DoesNotExist:
            # Create a new user
            username = 'LI:%s' % profile.id
            user = User(username =  username)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            user.first_name, user.last_name = profile.firstname, profile.lastname
            #user.email = '%s@example.linkedin.com'%(person.id)
            user.save()
            userprofile = LinkedInUserProfile(user = user, linkedin_uid = profile.id)
            #userprofile.access_token = linkedin_access_token.key
            userprofile.headline = profile.headline
            userprofile.company = profile.company
            userprofile.location = profile.location
            userprofile.industry = profile.industry
            userprofile.profile_image_url = profile.picture_url
            userprofile.url = profile.profile_url
            userprofile.save()
            auth_meta = AuthMeta(user=user, provider='LinkedIn').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None

class TwitterBackend:
    """TwitterBackend for authentication
    """
    def authenticate(self, twitter_access_token):
        '''authenticates the token by requesting user information from twitter
        '''
        twitter = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, twitter_access_token)
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
            #user.email = '%s@example.twitter.com'%(userinfo.screen_name)
            user.save()
            userprofile = TwitterUserProfile(user = user, screen_name = screen_name)
            # userprofile.access_token = access_token.key
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
    def authenticate(self, request):

        """
        if not settings.FACEBOOK_API_KEY in request.COOKIES:
            logging.debug("Could not find FACEBOOK_API_KEY in Cookies")
            return None
        """

        facebook =  Facebook(settings.FACEBOOK_API_KEY,
                             settings.FACEBOOK_SECRET_KEY)
                             
        check = facebook.check_session(request)
        fb_user = facebook.users.getLoggedInUser()

        try:
            profile = FacebookUserProfile.objects.get(facebook_uid = str(fb_user))
            return profile.user
        except FacebookUserProfile.DoesNotExist:
            fb_data = facebook.users.getInfo([fb_user], ['uid', 'about_me', 'first_name', 'last_name', 'pic_big', 'pic', 'pic_small', 'current_location', 'profile_url'])
            if not fb_data:
                return None
            fb_data = fb_data[0]

            username = 'FB:%s' % fb_data['uid']
            #user_email = '%s@example.facebook.com'%(fb_data['uid'])
            user = User.objects.create(username = username)
            user.first_name = fb_data['first_name']
            user.last_name = fb_data['last_name']
            user.save()
            location = str(fb_data['current_location'])
            about_me = str(fb_data['about_me'])
            url = str(fb_data['profile_url'])
            fb_profile = FacebookUserProfile(facebook_uid = str(fb_data['uid']), user = user, profile_image_url = fb_data['pic'], profile_image_url_big = fb_data['pic_big'], profile_image_url_small = fb_data['pic_small'], location=location, about_me=about_me, url=url)
            fb_profile.save()
            auth_meta = AuthMeta(user=user, provider='Facebook').save()
            return user
        except Exception, e:
            print str(e)

        return None

    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
