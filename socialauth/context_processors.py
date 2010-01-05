from django.conf import settings

def facebook_api_key(request):
    return {
        'FACEBOOK_API_KEY': settings.FACEBOOK_API_KEY
    }
