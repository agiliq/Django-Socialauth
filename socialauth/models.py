from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection, transaction

class AuthMeta(models.Model):
    """Metadata for Authentication"""
    def __unicode__(self):
        return '%s - %s' % (self.user, self.provider)
    
    user = models.ForeignKey(User)
    provider = models.CharField(max_length = 200)
    is_email_filled = models.BooleanField(default = False)
    is_profile_modified = models.BooleanField(default = False)

class OpenidProfile(models.Model):
    """A class associating an User to a Openid"""
    openid_key = models.CharField(max_length=200,unique=True, db_index = True)
    
    user = models.ForeignKey(User, related_name='openid_profiles')
    is_username_valid = models.BooleanField(default = False)
    #Values which we get from openid.sreg
    email = models.EmailField()
    nickname = models.CharField(max_length = 100)
    
    
    def __unicode__(self):
        return unicode(self.openid_key)
    
    def __repr__(self):
        return unicode(self.openid_key)
    
class LinkedInUserProfile(models.Model):
    """
    For users who login via Linkedin.
    """
    linkedin_uid = models.CharField(max_length = 50, unique = True, db_index=True)

    user = models.ForeignKey(User, related_name='linkedin_profiles')

    def __str__(self):
            return "%s's profile" % self.user

class TwitterUserProfile(models.Model):
    """
    For users who login via Twitter.
    """
    screen_name = models.CharField(max_length = 200, unique = True, db_index = True)
    
    user = models.ForeignKey(User, related_name='twitter_profiles')

    def __str__(self):
            return "%s's profile" % self.user
        

class FacebookUserProfile(models.Model):
    """
    For users who login via Facebook.
    """
    facebook_uid = models.CharField(max_length = 20, unique = True, db_index = True)
    
    user = models.ForeignKey(User, related_name='facebook_profiles')

