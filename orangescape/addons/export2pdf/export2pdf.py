from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import conversion
import logging

class PDFHandler(webapp.RequestHandler):
    def get(self):
        if (self.request.get('mode') == 'test'):
            self.response.out.write('<form method="post">')
            self.response.out.write('<textarea name="content" id="content" style="height:500px; width:500px;"></textarea><br />')
            self.response.out.write('<input type="submit" />')
            self.response.out.write('</form>')

    def post(self):
        logging.info('processing %s ' % (self.request.url))
        content = self.request.get('src')
        asset = conversion.Asset("text/html", content, "Content.html")
        conversion_obj = conversion.Conversion(asset, "application/pdf")
        result = conversion.convert(conversion_obj)
        if result.assets:
            for asset in result.assets:
                self.response.headers['Content-Type'] = "application/pdf"
                self.response.out.write(asset.data)
        else:
            self.response.out.write('Error Code : %s <br/>Error Text : %s' % (result.error_code, result.error_text))

def main():
    application = webapp.WSGIApplication([('/export2pdf', PDFHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
