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
from levitas.lib.daemonize import AbstractDaemon
from levitas.handler import WSGIHandler


log = logging.getLogger("levitas.server.baseServer")


class BaseServer(AbstractDaemon):
    """
    Base Server Class.
    
    Example SETTINGS entry
    ======================
        # Server address
        httpserver_address = ("127.0.0.1", 8080)
    """
    backlog = 128
    
    def __init__(self):
        settings = Settings()
        
        if hasattr(settings, "httpserver_address"):
            self.server_address = settings.httpserver_address
        else:
            self.server_address = ("127.0.0.1", 8080)
        
        log.info("Start server %s:%d [%d]" % (self.server_address[0],
                                              self.server_address[1],
                                              os.getpid()))
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
                
        self.app = WSGIHandler()
            
    def start(self):
        pass
            
    def stop(self):
        os._exit(0)
