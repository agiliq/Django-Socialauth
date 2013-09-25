from django.conf.urls.defaults import *
from openid_consumer.views import complete, signout
from django.views.generic.base import TemplateView

#Login Views
urlpatterns = patterns('socialauth.views',
    url(r'^facebook_login/xd_receiver.htm$', TemplateView.as_view(template_name='socialauth/xd_receiver.htm'), name='socialauth_xd_receiver'),
    url(r'^facebook_login/$', 'facebook_login', name='socialauth_facebook_login'),
    url(r'^facebook_login/done/$', 'facebook_login_done', name='socialauth_facebook_login_done'),
    url(r'^login/$', 'login_page', name='socialauth_login_page'),
    url(r'^openid_login/$', 'openid_login_page', name='socialauth_openid_login_page'),
    url(r'^twitter_login/$', 'twitter_login', name='socialauth_twitter_login'),
    url(r'^twitter_login/done/$', 'twitter_login_done', name='socialauth_twitter_login_done'),
    url(r'^linkedin_login/$', 'linkedin_login', name='socialauth_linkedin_login'),
    url(r'^linkedin_login/done/$', 'linkedin_login_done', name='socialauth_linkedin_login_done'),
    url(r'^yahoo_login/$', 'yahoo_login', name='socialauth_yahoo_login'),
    url(r'^yahoo_login/complete/$', complete, name='socialauth_yahoo_complete'),
    url(r'^gmail_login/$', 'gmail_login', name='socialauth_google_login'),
    url(r'^gmail_login/complete/$', complete, name='socialauth_google_complete'),
    url(r'^openid/$', 'openid_login', name='socialauth_openid_login'),
    url(r'^openid/complete/$', complete, name='socialauth_openid_complete'),
    url(r'^openid/signout/$', signout, name='openid_signout'),
    url(r'^openid/done/$', 'openid_done', name='openid_openid_done'),
    url(r'^github_login/$', 'github_login', name='github_login'),
    url(r'github_login/done/$', 'github_login_done', name='github_login_done'),
    url(r'^foursquare_login/$', 'foursquare_login', name='foursquare_login'),
    url(r'^foursquare_login/done/$', 'foursquare_login_done', name='foursquare_login_done'),
)

#Other views.
urlpatterns += patterns('socialauth.views',
    url(r'^$', 'login_page', name='socialauth_index'),
    url(r'^done/$', 'signin_complete', name='socialauth_signin_complete'),
    url(r'^edit/profile/$', 'editprofile',  name='socialauth_editprofile'),
    url(r'^logout/$', 'social_logout',  name='socialauth_social_logout'),
)

