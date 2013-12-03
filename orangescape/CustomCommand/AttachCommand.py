# AttachCommand.py
# Anbarasan <nasarabna@gmail.com>
# Custom Command to Copy Attachment from one record to another
# Params:
#    Source      : The SheetId of the record from which to copy the attachment
#    Target      : The SheetId of the record to which the attachment is to be copied
#    fileName    : The file name of the attachment as available in source record

import logging
from orangescape.model.server.Custom import CustomCommand
from orangescape.model.server.gae.GFSModels import Attachment, BlobPart
 
class CopyAttachment(CustomCommand):
   
    def enter(self):
        params = self.getParams()
       
        self.src_key = params['Source'].strip()
        self.tgt_key = params['Target'].strip()
        self.filename = params['fileName'].strip()
       
        logging.info("Copying Attachment from Sheet %s to Sheet %s" % (self.src_key, self.tgt_key))
       
        self.get()
        self.duplicate()
       
        self.update({'Attachment':self.filename})
       
        logging.info("Completed Copying Attachment from Sheet %s to Sheet %s" % (self.src_key, self.tgt_key))
   
    def get(self):
        # Get attachment from datastore
        self.attachment = Attachment().get_by_key_name(self.src_key)
        #self.blobpart = self.attachment.blobParts.get()
        #This above way does not get all attachments.
        self.blobparts = BlobPart.all().filter('blobEntity =', self.attachment).run()
       
    def duplicate(self):
        # duplicate the attachment
        attachment = Attachment()
        attachment._key_name = self.tgt_key
        attachment.put()
       
        #duplicate the file parts
        for blobpart in self.blobparts:
            new_blobpart = BlobPart(parent=attachment)
            new_blobpart.blobEntity = attachment
            new_blobpart.content = blobpart.content
            new_blobpart.partNo = blobpart.partNo
            new_blobpart.put()
