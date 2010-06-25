"""
LinkedIn OAuth Api Access 
Version: 0.01
License: MIT
Author: Max Lynch <max@mendotasoft.com>
Website: http://mendotasoft.com, http://maxlynch.com
Date Release: 11/23/2009

Enjoy!
"""

import hashlib
import urllib2
import httplib

import time

from xml.dom.minidom import parseString

import oauth.oauth as oauth

class LinkedIn():
    LI_SERVER = "api.linkedin.com"
    LI_API_URL = "https://api.linkedin.com"

    REQUEST_TOKEN_URL = LI_API_URL + "/uas/oauth/requestToken"
    AUTHORIZE_URL = LI_API_URL + "/uas/oauth/authorize"
    ACCESS_TOKEN_URL = LI_API_URL + "/uas/oauth/accessToken"



    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        self.connection = httplib.HTTPSConnection(self.LI_SERVER)
        self.consumer = oauth.OAuthConsumer(api_key, secret_key)
        self.sig_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

        self.status_api = StatusApi(self)
        self.connections_api = ConnectionsApi(self)

    def getRequestToken(self, callback):
        """
        Get a request token from linkedin
        """
        oauth_consumer_key = self.api_key

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                        callback=callback,
                        http_url = self.REQUEST_TOKEN_URL)
        oauth_request.sign_request(self.sig_method, self.consumer, None)


        self.connection.request(oauth_request.http_method,
                        self.REQUEST_TOKEN_URL, headers = oauth_request.to_header())
        response = self.connection.getresponse().read()
        
        token = oauth.OAuthToken.from_string(response)
        return token

    def getAuthorizeUrl(self, token):
        """
        Get the URL that we can redirect the user to for authorization of our
        application.
        """
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url = self.AUTHORIZE_URL)
        return oauth_request.to_url()

    def getAccessToken(self, token, verifier):
        """
        Using the verifier we obtained through the user's authorization of
        our application, get an access code.

        Note: token is the request token returned from the call to getRequestToken

        @return an OAuthToken object with the access token.  Use it like this:
                token.key -> Key
                token.secret -> Secret Key
        """
        token.verifier = verifier
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, verifier=verifier, http_url=self.ACCESS_TOKEN_URL)
        oauth_request.sign_request(self.sig_method, self.consumer, token)
        
        # self.connection.request(oauth_request.http_method, self.ACCESS_TOKEN_URL, headers=oauth_request.to_header()) 
        self.connection.request(oauth_request.http_method, oauth_request.to_url()) 
        response = self.connection.getresponse().read()
        return oauth.OAuthToken.from_string(response)

    """
    More functionality coming soon...
    """

class LinkedInApi():
    def __init__(self, linkedin):
        self.linkedin = linkedin

    def doApiRequest(self, url, access_token):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.linkedin.consumer, token=access_token, http_url=url)
        oauth_request.sign_request(self.linkedin.sig_method, self.linkedin.consumer, access_token)
        self.linkedin.connection.request(oauth_request.http_method, url, headers=oauth_request.to_header())
        return self.linkedin.connection.getresponse().read()


class StatusApi(LinkedInApi):
    STATUS_SELF_URL = LinkedIn.LI_API_URL + "/v1/people/~:(current-status)"
    
    def __init__(self, linkedin):
        LinkedInApi.__init__(self, linkedin)
    
    def getMyStatus(self, access_token):
        return self.doApiRequest(self.STATUS_SELF_URL, access_token)

class ProfileApi(LinkedInApi):
    """
    Get a LinkedIn Profile
    """
    PROFILE_SELF = LinkedIn.LI_API_URL + r"/v1/people/~:(id,first-name,last-name,headline,industry,picture-url,site-standard-profile-request)"
    
    def __init__(self, linkedin):
        LinkedInApi.__init__(self, linkedin)

    def getMyProfile(self, access_token):
        xml = self.doApiRequest(self.PROFILE_SELF, access_token)
        dom = parseString(xml)
        personDom = dom.getElementsByTagName('person')

        p = personDom[0]

        fn=ln=picurl=headline=company=industry=profurl=""

        try:
            id = p.getElementsByTagName('id')[0].firstChild.nodeValue
            fn = p.getElementsByTagName('first-name')[0].firstChild.nodeValue
            ln = p.getElementsByTagName('last-name')[0].firstChild.nodeValue
            picurl = p.getElementsByTagName('picture-url')[0].firstChild.nodeValue

            headline = p.getElementsByTagName('headline')[0].firstChild.nodeValue
            if ' at ' in headline:
                company = headline.split(' at ')[1]
            industry = p.getElementsByTagName('industry')[0].firstChild.nodeValue
            #location = p.getElementsByTagName('industry')[0].firstChild.nodeValue
            profurl = p.getElementsByTagName('url')[0].firstChild.nodeValue
        except:
            pass

        person = Person()
        person.id = id
        person.firstname = fn
        person.lastname = ln
        person.headline = headline
        person.company = company
        person.industry = industry
        person.picture_url = picurl
        person.profile_url = profurl

        return person

class ConnectionsApi(LinkedInApi):
    """
    How to get all of a user's connections:

            Note: This should happen after the linkedin redirect.  verifier is passed
            by LinkedIn back to your redirect page

            li = LinkedIn(LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET)

            tokenObj = oauth.OAuthToken(requestTokenKey, requestTokenSecret)
            access_token = li.getAccessToken(tokenObj, verifier)

            connections = li.connections_api.getMyConnections(access_token)

            for c in connections:
                    # Access c.firstname, c.lastname, etc.
    """

    CONNECTIONS_SELF = LinkedIn.LI_API_URL + "/v1/people/~/connections"
    def __init__(self, linkedin):
        LinkedInApi.__init__(self, linkedin)
        
    def getMyConnections(self, access_token):
        xml = self.doApiRequest(self.CONNECTIONS_SELF, access_token)
        dom = parseString(xml)
        peopleDom = dom.getElementsByTagName('person')

        people = []

        for p in peopleDom:
            try:
                fn = p.getElementsByTagName('first-name')[0].firstChild.nodeValue
                ln = p.getElementsByTagName('last-name')[0].firstChild.nodeValue
                headline = p.getElementsByTagName('headline')[0].firstChild.nodeValue
                company = headline.split(' at ')[1]
                industry = p.getElementsByTagName('industry')[0].firstChild.nodeValue
                #location = p.getElementsByTagName('industry')[0].firstChild.nodeValue
                person = Person()
                person.firstname = fn
                person.lastname = ln
                person.headline = headline
                person.company = company
                person.industry = industry
                people.append(person)
            except:
                continue
        return people

class Person():
    id = ""
    firstname = ""
    lastname = ""
    headline = ""
    company = ""
    location = None
    industry = ""
    picture_url = ""
    profile_url = ""

    def __str__(self):
        return "%s %s working at %s" % (self.firstname, self.lastname, self.company)

class Location():
    name = ""
    country = ""
