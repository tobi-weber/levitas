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

import logging
from wsgiref.simple_server import (make_server,
                                   WSGIServer,
                                   WSGIRequestHandler)
    
from .baseServer import BaseServer
from levitas.lib import utils


log = logging.getLogger("levitas.server.testServer")


class FapwsServer(BaseServer):
    """
    Test WSGI Server.
    
    Example SETTINGS entry
    ======================
        # Server address
        httpserver_address = ("127.0.0.1", 8080)
    """
            
    def start(self):
        try:
            httpd = make_server(self.server_address[0],
                                self.server_address[1],
                                self.app,
                                server_class=WSGIServer,
                                handler_class=WSGIRequestHandler)
            #httpd.socket.settimeout(0)
            httpd.serve_forever()
        except:
            utils.logTraceback()
        finally:
            log.info("HTTPD stopped")
            