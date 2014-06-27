#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Tobias Weber <tobi-weber@gmx.de>
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
    from urllib.request import  HTTPCookieProcessor  # python 3
except ImportError:
    import urllib2 as request  # python 2
    from urllib2 import HTTPCookieProcessor

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
    
    def __init__(self, port=8987):
        Thread.__init__(self)
        self._port = port
        self._running = True
        
    def run(self):
        httpd = make_server("localhost", self._port, WSGIHandler(),
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
        except:
            pass
        

class TestServer:
    
    def __init__(self, settings, port=8987):
        init_settings(settings)
        self.srv = WSGIServerThread(port=port)
        
    def start(self):
        self.srv.start()
        time.sleep(0.5)
        
    def stop(self):
        self.srv.stop()
        
        
class TestClient:
    
    def __init__(self, port=8987):
        cookie_handler = HTTPCookieProcessor()
        self.opener = request.build_opener(cookie_handler)
        self.url = "http://localhost:%d" % port
        
    def request(self, path, data=None, headers=None):
        headers = headers or {}
        try:
            if not path.startswith("/"):
                path = "/%s" % path
            url = self.url + path
            #print("Call url: %s" % url)
            req = request.Request(url,
                                  data=data,
                                  headers=headers)
            response = self.opener.open(req)
        except Exception as err:
            return err
        
        return response
        
    
    