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

import sys
import os
import imp
import time
from threading import Thread
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
try:
    from urllib import request  # python 3
except ImportError:
    import urllib2 as request  # python 2

from levitas.handler import WSGIHandler
from levitas.lib.settings import Settings


def init_settings(SETTINGS):
    module = imp.new_module("SETTINGS")
    exec(SETTINGS, module.__dict__)
    sys.modules["SETTINGS"] = module
    os.environ["LEVITAS_SETTINGS"] = "SETTINGS"
    Settings().import_module()
    

class TestWSGIServer(WSGIServer):
    
    def handle_error(self, request, client_address):
        pass
    
    
class TestWSGIRequestHandler(WSGIRequestHandler):
    
    def log_message(self, format, *args):  # @ReservedAssignment
        pass

    def get_stderr(self):
        return os.devnull
    

class WSGIServerThread(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self._running = True
        
    def run(self):
        httpd = make_server("localhost", 8987, WSGIHandler(),
                            server_class=TestWSGIServer,
                            handler_class=TestWSGIRequestHandler)
        httpd.socket.settimeout(0)
        while self._running:
            httpd.handle_request()
        
    def stop(self):
        opener = request.build_opener()
        url = "http://localhost:8987/"
        try:
            self._running = False
            req = request.Request(url)
            opener.open(req)
        except Exception as err:
            pass
        
        
        
        