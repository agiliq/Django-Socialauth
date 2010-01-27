import md5
import urllib
import time
try:
    import json as simplejson
except:
    from django.utils import simplejson

REST_SERVER = 'http://api.facebook.com/restserver.php'


def get_user_info(api_key, api_secret, cookies):
    user_info_params = {
                                        'method': 'Users.getInfo',
                                        'api_key': api_key,
                                        'call_id': time.time(),
                                        'v': '1.0',
                                        'uids': cookies[api_key + '_user'],
                                        'fields': 'uid,first_name,last_name,pic_small, name, current_location',
                                        'format': 'json',
                                    }

    user_info_hash = get_facebook_signature(api_key, api_secret, user_info_params)
    user_info_params['sig'] = user_info_hash            
    user_info_params = urllib.urlencode(user_info_params)
    user_info_response  = simplejson.load(urllib.urlopen(REST_SERVER, user_info_params))
    return user_info_response

def get_friends(api_key, api_secret, cookies):
    params = {
        'method': 'Friends.get',
        'api_key': api_key,
        'call_id': time.time(),
        'v': '1.0',
        'format': 'json',
    }
    return talk_to_fb(api_key, api_secret, params)

def get_friends_via_fql(api_key, api_secret, cookies):
    query = 'SELECT name, uid, pic_small  FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = %s)' % cookies[api_key + '_user']
    params = {
        'method': 'Fql.query',
        'session_key': cookies[api_key + '_session_key'],
        'query': query,
        'api_key': api_key,
        'call_id': time.time(),
        'v': '1.0',
        'uid': cookies[api_key + '_user'],
        'format': 'json',
    }
    return talk_to_fb(api_key, api_secret, params)

    
def talk_to_fb(api_key, api_secret, params):
    sig = get_facebook_signature(api_key, api_secret, params)
    params['sig'] = sig
    data = urllib.urlencode(params)
    response = simplejson.load(urllib.urlopen(REST_SERVER, data))
    return response

    
def get_facebook_signature(api_key, api_secret, values_dict, is_cookie_check=False):
        API_KEY = api_key
        API_SECRET = api_secret
        signature_keys = []
        for key in sorted(values_dict.keys()):
            if (is_cookie_check and key.startswith(API_KEY + '_')):
                signature_keys.append(key)
            elif (is_cookie_check is False):
                signature_keys.append(key)

        if (is_cookie_check):
            signature_string = ''.join(['%s=%s' % (x.replace(API_KEY + '_',''), values_dict[x]) for x in signature_keys])
        else:
            signature_string = ''.join(['%s=%s' % (x, values_dict[x]) for x in signature_keys])
        signature_string = signature_string + API_SECRET

        return md5.new(signature_string).hexdigest()
    
    
    
