from django.http import HttpResponse, HttpResponseRedirect, get_host
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import md5, re, time, urllib

import openid   
if openid.__version__ < '2.0.0':
    raise ImportError, 'You need python-openid 2.0.0 or newer'
elif openid.__version__ < '2.1.0':
    from openid.sreg import SRegRequest
else: 
    from openid.extensions.sreg import SRegRequest
    try:
        from openid.extensions.pape import Request as PapeRequest
    except ImportError:
        from openid.extensions import pape as openid_pape
        PapeRequest =  openid_pape.Request
    from openid.extensions.ax import FetchRequest as AXFetchRequest
    from openid.extensions.ax import AttrInfo

from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.yadis import xri

from util import OpenID, DjangoOpenIDStore, from_openid_response
from middleware import OpenIDMiddleware

from django.utils.html import escape

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()
		
next_url_re = re.compile('^/[-\w/]+$')

def is_valid_next_url(next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local 
    # path, not a complete URL.
    return bool(next_url_re.match(next))

def begin(request, redirect_to=None, on_failure=None, user_url=None, template_name='openid_consumer/signin.html'):
    on_failure = on_failure or default_on_failure
    trust_root = getattr(
        settings, 'OPENID_TRUST_ROOT', get_url_host(request) + '/'
    )
    
    
    # foo derbis.
    redirect_to = redirect_to or getattr(
        settings, 'OPENID_REDIRECT_TO',
        # If not explicitly set, assume current URL with complete/ appended
        get_full_url(request).split('?')[0] + 'complete/'
    )
    # In case they were lazy...
    if not redirect_to.startswith('http://') or redirect_to.startswith('https://'):
        redirect_to =  get_url_host(request) + redirect_to
    
    if request.GET.get('next') and is_valid_next_url(request.GET['next']):
        if '?' in redirect_to:
            join = '&'
        else:
            join = '?'
        redirect_to += join + urllib.urlencode({
            'next': request.GET['next']
        })
    if not user_url:
        user_url = request.REQUEST.get('openid_url', None)

    if not user_url:
        request_path = request.path
        if request.GET.get('next'):
            request_path += '?' + urllib.urlencode({
                'next': request.GET['next']
            })
        
        return render(template_name, {
            'action': request_path,
        }, RequestContext(request))
    
    if xri.identifierScheme(user_url) == 'XRI' and getattr(
        settings, 'OPENID_DISALLOW_INAMES', False
        ):
        return on_failure(request, _('i-names are not supported'))
    
    consumer = Consumer(request.session, DjangoOpenIDStore())

    try:
        auth_request = consumer.begin(user_url)
    except DiscoveryFailure:
        return on_failure(request, _('The OpenID was invalid'))
    
    sreg = getattr(settings, 'OPENID_SREG', False)
    
    if sreg:
        s = SRegRequest()        
        for sarg in sreg:
            if sarg.lower().lstrip() == "policy_url":
                s.policy_url = sreg[sarg]
            else:
                for v in sreg[sarg].split(','):
                    s.requestField(field_name=v.lower().lstrip(), required=(sarg.lower().lstrip() == "required"))
        auth_request.addExtension(s)  
    
    pape = getattr(settings, 'OPENID_PAPE', False)

    if pape:
        if openid.__version__ <= '2.0.0' and openid.__version__ >= '2.1.0':
            raise ImportError, 'For pape extension you need python-openid 2.1.0 or newer'
        p = PapeRequest()
        for parg in pape:
            if parg.lower().strip() == 'policy_list':
                for v in pape[parg].split(','):
                    p.addPolicyURI(v)
            elif parg.lower().strip() == 'max_auth_age':
                p.max_auth_age = pape[parg]
        auth_request.addExtension(p)
    
    OPENID_AX_PROVIDER_MAP = getattr(settings, 'OPENID_AX_PROVIDER_MAP', {})
    
    openid_provider = 'Google' if 'google' in request.session.get('openid_provider', '') else 'Default'
    ax = OPENID_AX_PROVIDER_MAP.get(openid_provider)
    
    if ax:
        axr = AXFetchRequest()
        for attr_name, attr_url in ax.items():
            # axr.add(AttrInfo(i['type_uri'], i['count'], i['required'], i['alias']))
            axr.add(AttrInfo(attr_url, required=True)) # setting all as required attrs
        auth_request.addExtension(axr)
    
    redirect_url = auth_request.redirectURL(trust_root, redirect_to)
    
    return HttpResponseRedirect(redirect_url)

def complete(request, on_success=None, on_failure=None, failure_template='openid_consumer/failure.html'):
    
    on_success = on_success or default_on_success
    on_failure = on_failure or default_on_failure
    
    consumer = Consumer(request.session, DjangoOpenIDStore())
    #dummydebug
    #for r in request.GET.items():
    #    print r

    # JanRain library raises a warning if passed unicode objects as the keys, 
    # so we convert to bytestrings before passing to the library
    query_dict = dict([
        (k.encode('utf8'), v.encode('utf8')) for k, v in request.REQUEST.items()
    ])

    url = get_url_host(request) + request.path
    openid_response = consumer.complete(query_dict, url)
    if openid_response.status == SUCCESS:
        return on_success(request, openid_response.identity_url, openid_response)
    elif openid_response.status == CANCEL:
        return on_failure(request, _('The request was cancelled'), failure_template)
    elif openid_response.status == FAILURE:
        return on_failure(request, openid_response.message, failure_template)
    elif openid_response.status == SETUP_NEEDED:
        return on_failure(request, _('Setup needed'), failure_template)
    else:
        assert False, "Bad openid status: %s" % openid_response.status

def default_on_success(request, identity_url, openid_response):
    if 'openids' not in request.session.keys():
        request.session['openids'] = []
    
    # Eliminate any duplicates
    request.session['openids'] = [
        o for o in request.session['openids'] if o.openid != identity_url
    ]
    request.session['openids'].append(from_openid_response(openid_response))
    
    # Set up request.openids and request.openid, reusing middleware logic
    OpenIDMiddleware().process_request(request)
    
    next = request.GET.get('next', '').strip()
    if not next or not is_valid_next_url(next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
    
    return HttpResponseRedirect(next)

def default_on_failure(request, message, template_name='openid_consumer/failure.html'):
    return render(template_name, {
        'message': message
    }, 		RequestContext(request))

def signout(request):
    request.session['openids'] = []
    next = request.GET.get('next', '/')
    if not is_valid_next_url(next):
        next = '/'
    return HttpResponseRedirect(next)
