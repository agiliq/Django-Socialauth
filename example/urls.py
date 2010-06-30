from django.conf.urls.defaults import *
from models import Post

urlpatterns = patterns('django.views.generic.date_based',
  url(r'^$', 'archive_index',
    { 'queryset' : Post.objects.all(), 'date_field' : 'date', }
  ),
)

