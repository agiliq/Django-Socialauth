from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection, transaction

class AuthMeta(models.Model):
    """Metadata for Authentication"""
    def __unicode__(self):
        return '%s - %s' % (self.user, self.provider)
    
    user = models.OneToOneField(User)
    provider = models.CharField(max_length = 30)
    is_email_filled = models.BooleanField(default = False)
    is_profile_modified = models.BooleanField(default = False)

class OpenidProfile(models.Model):
    """A class associating an User to a Openid"""
    openid_key = models.CharField(max_length=200,unique=True)
    
    user = models.ForeignKey(User)
    is_username_valid = models.BooleanField(default = False)
    #Values which we get from openid.sreg
    email = models.EmailField()
    nickname = models.CharField(max_length = 100)
    
    
    def __unicode__(self):
        return unicode(self.openid_key)
    
    def __repr__(self):
        return unicode(self.openid_key)
    

class TwitterUserProfile(models.Model):
    """
    For users who login via Twitter.
    """
    screen_name = models.CharField(max_length = 200, unique = True)
    
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=255, blank=True, null=True, editable=False)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=160, blank=True, null=True)

    def __str__(self):
            return "%s's profile" % self.user
        

class FacebookUserProfile(models.Model):
    """
    For users who login via Facebook.
    """
    facebook_uid = models.CharField(max_length = 20, unique = True)
    
    user = models.ForeignKey(User)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    about_me = models.CharField(max_length=160, blank=True, null=True)
    
    



