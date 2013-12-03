# auth.py
from config import CLIENTID, CLIENTSECRET, REDIRECTURI
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

import json, logging

# storage for access credentials
class CredentialStore(ndb.Model):
    refreshToken    = ndb.StringProperty()                      
    accessToken     = ndb.StringProperty()
    expiresIn       = ndb.DateTimeProperty()
    createdAt       = ndb.DateTimeProperty(auto_now_add=True)
    
# API access points
BASEURL         = "https://accounts.google.com"
AUTHENDPOINT    = "/o/oauth2/auth"
TOKENENDPOINT   = "/o/oauth2/token"

class Authorize():
    def __init__(self):
        self.accessToken    = None
        self.refreshToken   = None
        self.expiresIn      = None
        self.TokenType      = None
        self.store          = self.getCredentialStore()
        
    def getCredentialStore(self):
        """ retrieve stored credentials """
        stores = CredentialStore().query()
        store = None
        for s in stores:
            store = s
            
        if store is None:
            store = CredentialStore()
            
        return store
            
    def getAuthorizationURL(self):
        """ return Authorization URL """
        SCOPE           = "https://www.googleapis.com/auth/calendar"
        
        requestURL = BASEURL + AUTHENDPOINT 
        requestURL += "?scope=" + SCOPE + "&state=authorization&redirect_uri=" + REDIRECTURI 
        requestURL += "&response_type=code&client_id=" + CLIENTID + "&approval_prompt=force&access_type=offline"
        return requestURL
        
    def authorize(self, authorizationCode):
        """ get authorized tokens to use with google apis """
        REDIRECTURI     = "http://speedy-code-376.appspot.com/oauth2callback"
        
        requestURL = BASEURL + TOKENENDPOINT
        
        logging.debug("Requesting Access Token : %s" % (requestURL))
        
        request = Request(requestURL)
        request.get_method = lambda: "POST"
        data = {  'client_id':CLIENTID
                , 'client_secret':CLIENTSECRET
                , 'redirect_uri':REDIRECTURI
                , 'code':authorizationCode
                , 'grant_type':'authorization_code'
                }
            
        self.fetch(request, data)
        
    def storeAuthorization(self, store=None):
        """ store the obtained authorization tokens in the datastore for future usage """
        if store is None:
            store = self.store
        
        store.refreshToken = self.refreshToken
        store.accessToken  = self.accessToken
        store.expiresIn    = datetime.now()+timedelta(seconds=self.expiresIn)
        store.put()
        
    def getAccessToken(self, authorizationCode=None):
        """ returns the accessToken """
        
        if authorizationCode is None:
            self.refreshAccessToken()
        else:
            self.authorize(authorizationCode)
        
        return self.store.accessToken
        
    def hasTokenExpired(self):
        """ check if the accessToken is valid or expired """
        store = self.store
        if store is not None:
            if (datetime.now() >= (store.expiresIn + timedelta(seconds = -60))):
                return True
        
        return False
        
    def refreshAccessToken(self):
        """ checks if the accessToken has expired and
            returns the accessToken based on refresh Token """
        
        if self.hasTokenExpired():
            requestURL = BASEURL + TOKENENDPOINT
            
            logging.info("Requesting Access Token : %s" % (requestURL))
            
            request = Request(requestURL)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            request.get_method = lambda: "POST"
            
            data = {  'client_id':CLIENTID
                    , 'client_secret':CLIENTSECRET
                    , 'refresh_token':self.store.refreshToken
                    , 'grant_type':'refresh_token'
                    }
            
            self.fetch(request, data)
            
    def fetch(self, request, data):
        """ requests and gets token information """
        logging.debug(data)
        try:
            response = urlopen(request, urlencode(data))
            result = json.loads(response.read())
            
            try:
                self.refreshToken   = result['refresh_token']
            except:
                self.refreshToken   = self.store.refreshToken
                
            self.accessToken    = result['access_token']
            self.expiresIn      = result['expires_in']
            self.TokenType      = result['token_type']
            
            self.storeAuthorization()
            
        except HTTPError, e:
            logging.error(e.read())
            raise
            
