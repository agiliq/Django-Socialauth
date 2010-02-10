from django.conf.urls.defaults import *
from commentor.views import leave_comment

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('socialauth.urls')),
    (r'^admin/', admin.site.urls), 
    (r'node/(?P<post_id>\d+)/$', 'blog.views.post'),
    (r'^$', leave_comment), 
)
from django.conf import settings

if settings.DEBUG:
    
    urlpatterns += patterns('',
        # This is for the CSS and static files:
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    
