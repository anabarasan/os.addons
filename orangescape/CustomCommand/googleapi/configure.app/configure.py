from google.appengine.ext import ndb

class CredentialStore(ndb.Model):
    refreshToken    = ndb.StringProperty()                      
    accessToken     = ndb.StringProperty()
    expiresIn       = ndb.DateTimeProperty()
    createdAt       = ndb.DateTimeProperty(auto_now_add=True)
    
from config import  CLIENTID, CLIENTSECRET, REDIRECTURI
from datetime import datetime, timedelta
import base64, json, logging, urllib, urllib2, webapp2

BASEURL         = "https://accounts.google.com"
AUTHENDPOINT    = "/o/oauth2/auth"
TOKENENDPOINT   = "/o/oauth2/token"

class MainHandler(webapp2.RequestHandler):
    def get(self):
        action = self.request.get('action')
        
        if (action == 'authorize'):
            self.authorize()
        else:
            self.response.out.write(
                """
                    <head>
                        <style type="text/css">
                            .classname {
                                -moz-box-shadow:inset 0px 1px 0px 0px #fed897;
                                -webkit-box-shadow:inset 0px 1px 0px 0px #fed897;
                                box-shadow:inset 0px 1px 0px 0px #fed897;
                                background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #f6b33d), color-stop(1, #d29105) );
                                background:-moz-linear-gradient( center top, #f6b33d 5%, #d29105 100% );
                                filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#f6b33d', endColorstr='#d29105');
                                background-color:#f6b33d;
                                -webkit-border-top-left-radius:20px;
                                -moz-border-radius-topleft:20px;
                                border-top-left-radius:20px;
                                -webkit-border-top-right-radius:20px;
                                -moz-border-radius-topright:20px;
                                border-top-right-radius:20px;
                                -webkit-border-bottom-right-radius:20px;
                                -moz-border-radius-bottomright:20px;
                                border-bottom-right-radius:20px;
                                -webkit-border-bottom-left-radius:20px;
                                -moz-border-radius-bottomleft:20px;
                                border-bottom-left-radius:20px;
                                text-indent:0;
                                border:1px solid #eda933;
                                display:inline-block;
                                color:#ffffff;
                                font-family:Arial;
                                font-size:15px;
                                font-weight:bold;
                                font-style:normal;
                                height:65px;
                                line-height:65px;
                                width:131px;
                                text-decoration:none;
                                text-align:center;
                                text-shadow:1px 1px 0px #cd8a15;
                            }
                            .classname:hover {
                                background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #d29105), color-stop(1, #f6b33d) );
                                background:-moz-linear-gradient( center top, #d29105 5%, #f6b33d 100% );
                                filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#d29105', endColorstr='#f6b33d');
                                background-color:#d29105;
                            }
                            .classname:active {
                                position:relative;
                                top:1px;
                            }
                        </style>
                    </head>
                    <body>
                        <br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
                        <div style="width:100%; text-align:center;">
                            <a class='classname' href='?action=authorize'> Authorize </a>
                        </div>
                    </body>
                """
            )
        
    def authorize(self):
        SCOPE = "https://www.googleapis.com/auth/calendar"
        
        requestURL = BASEURL + AUTHENDPOINT 
        requestURL += "?scope=" + SCOPE + "&state=authorization&redirect_uri=" + REDIRECTURI 
        requestURL += "&response_type=code&client_id=" + CLIENTID + "&approval_prompt=force&access_type=offline"
        self.redirect(requestURL)
        
class oAuthHandler(webapp2.RequestHandler):
    def get(self):
        error           = self.request.get("error")
        state           = self.request.get("state")
        code            = self.request.get("code")          # Authorization Code
        
        logging.debug("Error : %s<br/>State : %s<br/>Code : %s<br/>" % (error, state, code))
        
        if (error == "") or (error is not None):
            self.AuthorizationCode = code
            self.getAccess()
            self.storeAccess()
            self.redirect('/')
        else:
            self.response.out.write("ERROR : %s" % (error))
    
    def getAccess(self):
        requestURL = BASEURL + TOKENENDPOINT
        
        logging.info("Requesting Access Token : %s" % (requestURL))
        
        request = urllib2.Request(requestURL)
        request.get_method = lambda: "POST"
        
        data = {  'client_id':CLIENTID
                , 'client_secret':CLIENTSECRET
                , 'redirect_uri':REDIRECTURI
                , 'code':self.AuthorizationCode
                , 'grant_type':'authorization_code'
        }
        
        try:
            response = urllib2.urlopen(request, urllib.urlencode(data))
            result = json.loads(response.read())
            
            self.accessToken    = result['access_token']
            self.refreshToken   = result['refresh_token']
            self.expiresIn      = result['expires_in']
            self.TokenType      = result['token_type']
        except HTTPError, e:
            logging.error(e.read())
            raise
        
    def storeAccess(self):
        stores = CredentialStore().query()
        store = None
        for s in stores:
            store = s
            
        if store is None:
            store = CredentialStore()
        
        store.refreshToken = self.refreshToken
        store.accessToken  = self.accessToken
        store.expiresIn    = datetime.now()+timedelta(seconds=self.expiresIn)
        store.put()
        
app = webapp2.WSGIApplication([
                        ('/', MainHandler),
                        ('/oauth2callback', oAuthHandler),
                        ], debug=True)
