from django.conf import settings


def facebook_api_key(request):
    FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', '')
    FACEBOOK_REQUEST_PERMISSIONS = getattr(settings, 'FACEBOOK_REQUEST_PERMISSIONS', '')
    if FACEBOOK_APP_ID:
        return { 'FACEBOOK_APP_ID': FACEBOOK_APP_ID, 
                 'login_button_perms': ' '.join(FACEBOOK_REQUEST_PERMISSIONS), }
    else:
        return {}
