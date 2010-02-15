from django.conf.urls.defaults import *
from commentor.views import leave_comment

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('socialauth.urls')),
    (r'^admin/', admin.site.urls), 
    #(r'^$', leave_comment), 
    (r'^$', 'socialauth.views.signin_complete'), 

>>>>>>> ecd9f42fc391a068637dac06a326a1eb6d1b3f0f:urls.py
)
from django.conf import settings

if settings.DEBUG:
    
    urlpatterns += patterns('',
        # This is for the CSS and static files:
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    
