# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Tobias Weber <tobi-weber@gmx.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging

from levitas.lib.settings import Settings
from levitas.lib import utils
from levitas.lib.daemonize import AbstractDaemon
from handler import WSGIHandler


log = logging.getLogger("levitas.httpd")


class LevitasServer(AbstractDaemon):
    """
    WSGI Server.
    
    Example settings entry
    ======================
        # Server address
        httpserver_address = ("127.0.0.1", 8080)
    """
    backlog = 128
    
    def __init__(self):
        settings = Settings()
        
        settings.require("httpserver_address",
                         'httpserver_address = ("127.0.0.1", 8080)')
        self.server_address = settings.httpserver_address
        
        self.ssl = False
        if hasattr(settings, "httpserver_ssl"):
            self.ssl = settings.httpserver_ssl
            if settings.httpserver_ssl:
                settings.require("httpserver_certfile",
                                 'httpserver_certfile = "/path/to/certfile"')
                settings.require("httpserver_keyfile",
                                 'httpserver_keyfile = "/path/to/keyfile"')
                self.certfile = settings.httpserver_certfile
                self.keyfile = settings.httpserver_keyfile
                
        self.instances = []
            
    def start(self):
        try:
            from twisted.internet import epollreactor
            epollreactor.install()
        except:
            pass
        from twisted.web.server import Site
        from twisted.web.wsgi import WSGIResource
        from twisted.internet import reactor
        try:
            application = WSGIHandler()
            resource = WSGIResource(reactor,
                                    reactor.getThreadPool(),  # @UndefinedVariable
                                    application)

            port = self.server_address[1]
            site = Site(resource)
            backlog = self.backlog
            interface = self.server_address[0]
            
            log.info("Listen on %s:%s" % (interface, str(port)))
            
            if self.ssl:
                from twisted.internet import ssl
                sslContext = ssl.DefaultOpenSSLContextFactory(self.keyfile,
                                                              self.certfile)
                reactor.listenSSL(port, site,  # @UndefinedVariable
                                  contextFactory = sslContext,
                                  backlog=backlog,
                                  interface=interface)

            else:
                reactor.listenTCP(port, site,  # @UndefinedVariable
                                  backlog=backlog,
                                  interface=interface)
                
            reactor.run()  # @UndefinedVariable
        except:
            utils.logTraceback()
        finally:
            log.info("HTTPD stopped")
            #os._exit(0)
            
    def stop(self):
        os._exit(0)
            
            