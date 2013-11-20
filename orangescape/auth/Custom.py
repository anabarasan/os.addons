# Custom.py
import logging
from appconfig import env, GAE, GAESQL, ENTERPRISE
from orangescape.model.server.UserAuthentication import UserAuthentication

def authenticate(self, controller):
    authenticated = False
    resultDict = {"authenticated":authenticated}
    
    userEmail = controller.request.get("userid")
    password = controller.request.get("password")    
    authentication=UserAuthentication(controller.session,userEmail)
    userinfo = authentication.getUser(userEmail)
    
    if userinfo and (userinfo.getValue("UserId") == userEmail) and (userinfo.getValue("PassPhrase") == password):
        authenticated = True
    
    if authenticated:
        resultDict["authenticated"] = authenticated
        resultDict["userEmail"] = userEmail
        
    return resultDict
        
def ClassFactory(className, BaseClass):
    #http://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class
    def __init__(self):
        BaseClass.__init__(self)
    newclass = type(className, (BaseClass,),{"__init__": __init__, "authenticate" : authenticate})
    return newclass
    
class SelfAuthenticator:
    def authenticate(self, controller):
        if env in (GAE , GAESQL):
            from GAEAuth import GAEAbstractAuth as BaseAuthenticator
        elif env == ENTERPRISE:
            from EnterpriseAuth import EnterpriseAbstractAuth as BaseAuthenticator
        
        return ClassFactory('Authenticator', BaseAuthenticator)().authenticate(controller)
