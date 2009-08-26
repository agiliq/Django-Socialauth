from django.conf.urls.defaults import *
from commentor.views import leave_comment
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('socialauth.urls')),
    (r'^$', leave_comment), 

)
