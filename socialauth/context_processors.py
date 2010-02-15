from django.conf import settings

def socialauth (request):
    return {'fb_api_key':settings.FACEBOOK_API_KEY,}

def facebook_api_key(request):
    return {
        'FACEBOOK_API_KEY': settings.FACEBOOK_API_KEY
    }
