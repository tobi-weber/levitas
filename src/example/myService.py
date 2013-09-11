# -*- coding: utf-8 -*-

from levitas.middleware.service import Service


class MyService(Service):
    
    def getMessage(self):
        # Return the message configured in service_attributes
        return self.msg
    
    def sendMessage(self, msg):
        client = self.middleware.remote_host
        return "Message from %s: %s" % (client, msg)
    
    def _prepare(self):
        """
        Method will be called after service class is instantiated.
        """
        pass
    
    def _complete(self):
        """
        Method will be called after service method is finished.
        """
        pass
    