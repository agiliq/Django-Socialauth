from django.conf.urls.defaults import *
from models import Post

urlpatterns = patterns('',
    url(r'^(?P<post_id>\d+)$', 'example.views.post_detail'),
    url(r'^$', 'django.views.generic.list_detail.object_list',
        { 'queryset' : Post.objects.all() }
    ),
)
