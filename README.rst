WARNING: This app is not maintained anymore
-------------------------------------------------
This repo is here for archive purposes, but unmaintained. There are much better social auth libraries.

* https://github.com/omab/django-social-auth/ 
* https://github.com/pennersr/django-allauth



What it does.
--------------

#. Allow logging in via various providers.
#. Import contacts from various third party sites, to find out which of your
   friends already use our service.

Logging In
----------

This is a application to enable authentication via various third party sites.
In particular it allows logging in via

#. Twitter
#. Gmail
#. Facebook
#. Yahoo(Essentially openid)
#. OpenId
#. Github
#. Foursquare

Libs you need to install
See requirements.txt
use `pip install -r requirements.txt` to install all dependencies at once
Note that you will probably require git and mercurial installed for pip to
fetch the requirements.

The API Keys are available from

* http://www.facebook.com/developers/createapp.php 
* https://developer.yahoo.com/dashboard/createKey.html
* https://www.google.com/accounts/ManageDomains
* http://twitter.com/oauth_clients 
* https://github.com/settings/applications/new
* https://developer.foursquare.com/overview/auth.html

How it works.
--------------

* **Openid**: Users need to provide their openid providers. Talk to the providers and
  login.
* **Yahoo**: Yahoo is an openid provider. Talk to Yahoo endpoints. (Endpoint: http://yahoo.com)
* **Google**: Google is a provider. Talk to them. (Endpoint: https://www.google.com/accounts/o8/id)
* **Facebook**: Facebook connect provides authentication framework.
* **Twitter**: We use Twitter Oauth for authentication. In theory, Oauth shouldn't be
  used for authentication. (It is an autorisation framework, not an authentication one),
  In practice it works pretty well. Once you have an access_token, and a name, essentially
  authenticated.
* **Github**:We use Github Oauth for authentication. As like Twitter, it works
  pretty well.
* **Foursquare**:We use Oauth2.0 for authenticating via foursquare.

References
----------

#. http://openid.net/developers/
#. http://developer.yahoo.com/openid/
#. http://code.google.com/apis/accounts/docs/OpenID.html
#. http://apiwiki.twitter.com/OAuth-FAQ
#. http://developers.facebook.com/connect.php
#. http://develop.github.com/p/oauth.html
#. https://developer.foursquare.com/overview/auth.html

Limitations
------------

As with all APIs, we are limited by the amount of data which the API provider
provides us. For example, both Yahoo and Google provide extremely limited data
about the autheticated subscriber. Twitter and Facebook provide a lot of details,
but not the email. Different Openid providers are free to provide [different
amounts of data](http://openid.net/specs/openid-simple-registration-extension-1_0.html).

How it works.
--------------

#. For all providers(except Facebook) there are two urls and views. (start and done)
#. Start sets up the required tokens, and redirects and hands off to the correct
   provider.
#. Provider handles authentication on their ends, and hands off to Us, providing
   authorization tokens.
#. In done, we check if the user with these details already exists, if yes, we
   log them in. Otherwise we create a new user, and log them in.

For all of these, we use standard django authenication system, with custom
auth_backends, hence all existing views, and decorators as login_required
will work as expected.

Urls
-----

* /login/ Login page. Has all the login options
* /openid_login/ AND /openid_login/done/
* /yahoo_login/ AND /yahoo_login/done/
* /gmail_login/ AND /gmail_login/done/
* /twitter_login/ AND /twitter_login/done/
* /facebook_login/done/ We dont have a start url here, as the starting tokens are
  set in a popup.
* /github_login/ AND /github_login/done/
* /foursquare_login/ AND /foursquare_login/done/

Implementation
---------------

#. Install required libraries.
#. Get tokens and populate in localsettings.py
#. Set the token callback urls correctly at Twitter, Facebook, Github and Foursquare.
#. Set the authentication_backends to the providers you are using.
