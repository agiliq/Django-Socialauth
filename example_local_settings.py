OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_SREG = {"requred": "nickname, email",
               "optional":"postcode, country",
               "policy_url": ""}

OPENID_AX = [{"type_uri": "email",
              "count": 1,
              "required": False,
              "alias": "email"},
             {"type_uri": "fullname",
              "count":1 ,
              "required": False,
              "alias": "fullname"}]

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )






