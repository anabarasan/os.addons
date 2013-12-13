# Custom.py
import logging
from appconfig import env, GAE, GAESQL, ENTERPRISE
from orangescape.model.server.UserAuthentication import UserAuthentication

if env in (GAE , GAESQL):
    from GAEAuth import GAEAbstractAuth as BaseAuthenticator
elif env == ENTERPRISE:
    from EnterpriseAuth import EnterpriseAbstractAuth as BaseAuthenticator
else:
    from Dummy import DummyAuthenticator as BaseAuthenticator
    
class SelfAuthenticator(BaseAuthenticator):
    def authenticate(self, controller):
        authenticated = False
        resultDict = {"authenticated":authenticated}
        
        userEmail = controller.request.get("userid")
        password = controller.request.get("password")    
        authentication=UserAuthentication(controller.session,userEmail)
        userinfo = authentication.getUser(userEmail)
        
        if userinfo and (userinfo.getValue("UserId") == userEmail) and (userinfo.getValue("PassPhrase") == password):
            logging.info("Login successful for user %s" % (userinfo.getValue("UserId")))
            authenticated = True
        
        if authenticated:
            resultDict["authenticated"] = authenticated
            resultDict["userEmail"] = userEmail
        else:
            logging.error("UnSuccessful login attempt for user %s" % (userEmail))
            controller.request.__setattr__("errorMessage", "invalid userid or password")
            
        return resultDict
