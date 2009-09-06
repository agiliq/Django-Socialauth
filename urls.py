from django.conf.urls.defaults import *
from commentor.views import leave_comment

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('socialauth.urls')),
    (r'^admin/$', admin.site.urls), 
    (r'^$', leave_comment), 

)
