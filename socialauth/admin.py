from socialauth.models import AuthMeta, UserAssociation, TwitterUserProfile
from socialauth.models import GmailContact, YahooContact, TwitterContact, \
                            FacebookContact, SocialProfile

from django.contrib import admin

admin.site.register(AuthMeta)
admin.site.register(UserAssociation)
admin.site.register(TwitterUserProfile)

admin.site.register(GmailContact)
admin.site.register(YahooContact)
admin.site.register(TwitterContact)
admin.site.register(FacebookContact)
admin.site.register(SocialProfile)



