from socialauth.models import AuthMeta, UserAssociation, TwitterUserProfile

from django.contrib import admin

admin.site.register(AuthMeta)
admin.site.register(UserAssociation)
admin.site.register(TwitterUserProfile)

