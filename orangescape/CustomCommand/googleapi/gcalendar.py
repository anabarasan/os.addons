# gcalendar.py 
# Anbarasan <nasarabna@gmail.com>
# Custom Command to create a google calendar event and send invites
# params : 
#    summary     : Title of the Event 
#    description : A small description of the Event
#    start       : start date of the event (YYYY-MM-DD)
#    end         : end date of the event should be startdate + 1 (YYYY-MM-DD)
#    attendees   : attendee email address, comma delimited

import json, logging, urllib, urllib2
from auth import Authorize
from config import APIKEY, CALENDARID
from orangescape.model.server.Custom import CustomCommand

INVITE = {
            "summary" : "<Summary>",
            "description" : "<description>",
            "reminders" : {
                "useDefault" : False,
                "overrides" : [
                    {
                        "method" : "email",
                        "minutes" : 10
                    }
                ]
            },
            "start" : {},
            "end" : {},
            "attendees" : []
        }


class CreateEvent(CustomCommand):
    def start(self):
        params = self.getParams()
        logging.debug("##########################")
        logging.debug(params)
        logging.debug(params.keys())
        logging.debug("##########################")
        
        self.invite = INVITE.copy()
        
        for key in params.keys():
            if (key == 'attendees'):
                attendeeList = []
                
                for attendee in params[key].split(","):
                    attendeeList.append({'email':attendee})
                    
                self.invite[key] = attendeeList
            elif (key == 'start') or (key == 'end'):
                # start and end dates are objects
                self.invite[key] = {"date": params[key]} 
            else:
                self.invite[key] = params[key]
        
        logging.info(self.invite)
        
    def enter(self):
        
        try:
            calendar = GoogleCalendar()
            calendar.insertEvent(CALENDARID,self.invite)
        except:
            raise
        

class GoogleCalendar():

    def authorize(self):
        """ Get Authorize token to use with the API """
        authorization = Authorize()
        self.accessToken = authorization.getAccessToken()
        
    def insertEvent(self, calenderId, event):
        """ Creates an Event in the given Calendar with the given details and notifies the attendes """
        
        self.authorize()
        
        AccessToken = self.accessToken
        requestURL = "https://www.googleapis.com/calendar/v3/calendars/%s/events?sendNotifications=true&key=%s&access_token=%s" % (calenderId, APIKEY, AccessToken)
        
        data = json.dumps(event)
        
        logging.info("Creating Event in Calendar %s => %s" % (calenderId, requestURL))
        request = urllib2.Request(requestURL)
        request.add_header('Content-Type', 'application/json')
        
        authorization = 'Bearer %s' % (AccessToken)
        request.add_header('Authorization', authorization)
        
        logging.debug(request)
        logging.debug(data)
        
        try:
            response = urllib2.urlopen(request, data)
            result = json.loads(response.read())
            
            logging.debug(result)
            
        except urllib2.HTTPError, e:
            logging.debug(e.read())
            raise
            
