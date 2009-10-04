from socialauth.models import AuthMeta, OpenidProfile, TwitterUserProfile, FacebookUserProfile

from django.contrib import admin

admin.site.register(AuthMeta)
admin.site.register(OpenidProfile)
admin.site.register(TwitterUserProfile)
admin.site.register(FacebookUserProfile)

