from django.conf.urls.defaults import *
from commentor.views import leave_comment

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^blog/', include('example.urls')),
    (r'^accounts/', include('socialauth.urls')),
    (r'^admin/', admin.site.urls), 
    #(r'^$', leave_comment), 
    (r'^$', 'socialauth.views.signin_complete'),
    (r'^comments/post/', 'example_comments.views.post_comment'),
    (r'comments/', include('django.contrib.comments.urls')),
)

from django.conf import settings
if settings.DEBUG:
    
    urlpatterns += patterns('',
        # This is for the CSS and static files:
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    
