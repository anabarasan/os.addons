# ProtegoTotalum.py

import logging
from google.appengine.ext import ndb
from GAEAuth import GAEAbstractAuth

# Model containing Identity Information
class identities(ndb.Model):
    FirstName       = ndb.StringProperty()
    LastName        = ndb.StringProperty()
    EmailAddress    = ndb.StringProperty()
    Password        = ndb.StringProperty()
    
# Model to store Session Information
class sessions(ndb.Model):
    EmailAddress    = ndb.StringProperty()
    LoggedInAt      = ndb.DateTimeProperty(auto_now_add=True)
    ExpiresAt       = ndb.DateTimeProperty()
    
class ProtegoTotalumAuthenticator(GAEAbstractAuth):
    def authenticate(self, controller):
        
        resultDict = {"authenticated":False}
        request = controller.request
        userEmail = controller.request.get("userid")
        password = controller.request.get("password")
        
        users = identities.query(identities.EmailAddress == userEmail) # Get the User Object with given Email Address
        authUser = None
        for user in users:
            authUser = user
            break
        
        if (authUser) and (authUser.Password == password): # If User exists check if password Matches
            logging.info("authentication successful for user %s" % (userEmail))
            resultDict["authenticated"] = True
            resultDict["userEmail"] = controller.request.get("userid")
        else:
            logging.error("UnSuccessful login attempt for user %s" % (userEmail))
            controller.request.__setattr__("errorMessage", "invalid userid or password")
        
        return resultDict
