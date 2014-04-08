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
from .factory import MiddlewareFactory
from .middleware.middleware import Middleware
from .signals import (application_instanciated,
                     application_called)


log = logging.getLogger("levitas.handler")


class WSGIHandler(object):
    """
    WSGIHandler for the levitas application.
    
    
    Example settings
    ================
        A url definition is a tuple with three parts:
        (r"/.*$", MiddlewareClass, {"arg": "value"})
            1. regular expression of the request path.
            2. middleware class.
            3. Arguments to instantiate the class.
        
        Example: 
        urls = [
            # (regular expression of the request path, middleware class,
            (r"^/json", JSONMiddleware, {"service_class": MyService}),
            (r"(?!/json/.*)^/.*$", AppMiddleware, {"path": "/path/to/app"})
       ]
       
       # Working directory of the wsgi application
       working_dir = "/path/to/working directory"
       
       # Custom path to the favicon
       favicon = "/path/to/favicon.ico"
    
    
    WSGI capable webservers
    ========================
       Apache:
           http://code.google.com/p/modwsgi/
            
       uwsgi:
           http://projects.unbit.it/uwsgi/
           uwsgi application server can also used with Apache and
           also with Nginx and others.
    
    
    Example wsgi script
    ===================
       import os
        
       from levitas.handler import WSGIHandler
        
       # Pythonpath to your settings module
       os.environ["LEVITAS_SETTINGS"] = "my_module.my_settings"
        
       application = WSGIHandler()
    """
       
    def __init__(self, logfile=None, logfilecount=0, verbose=False):
        if logfile is not None:
            self._initLogging(logfile, logfilecount, verbose)
        log.debug("WSGIHandler created %d" % os.getpid())
        
        self.settings = Settings()
        
        self.settings.require("urls",
            'urls = [(r"/$", StaticFileHandler, {"path": "/files/path")}), ]')
        
        if hasattr(self.settings, "favicon"):
            self.favicon = self.settings.favicon
        else:
            self.favicon = None
            
        # Send instanciated signal
        application_instanciated.send(self.__class__,
                                      application=self)
        
        self.factories = []
        for url in self.settings.urls:
            self.createFactory(url)
        
        if hasattr(self.settings, "working_dir"):
            log.info("Set workingdir to %s" % self.settings.working_dir)
            os.chdir(self.settings.working_dir)
    
    def addURLs(self, urls):
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            self.createFactory(url)
    
    def createFactory(self, url):
        regex = url[0]
        handler = url[1]
        if len(url) == 3:
            kwargs = url[2]
        else:
            kwargs = {}
        log.debug("MiddlewareFactory: %s, %s, %s" % (regex,
                                                     handler.__name__,
                                                     str(kwargs)))
        factory = MiddlewareFactory(regex, handler, **kwargs)
        self.factories.append(factory)
        
    def _error(self, environ, _startResponse, code):
        middleware = Middleware()
        middleware.initEnviron(environ, _startResponse)
        return middleware.responseError(code)
        
    def _initLogging(self, logfile=None, logfilecount=0, verbose=False):
        if logfile is None:
            return
        
        from logging.handlers import TimedRotatingFileHandler
        log = logging.getLogger()
        formatter = logging.Formatter("%(asctime)s - %(name)s "
                                  "- %(levelname)s - %(message)s")
        h = TimedRotatingFileHandler(logfile, when="midnight",
                                     backupCount=logfilecount)
        h.doRollover()
        
        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            
        h.setFormatter(formatter)
        log.addHandler(h)
        
    def __call__(self, environ, _startResponse):
        #log.debug("Application call %d" % os.getpid())
        
        # Send called signal
        application_called.send(self.__class__,
                                application=self,
                                environ=environ)
        
        # Send favicon
        if self.favicon:
            self.send_response(200)
            self.end_headers()
            try:
                f = open(self.settings.favicon)
                _startResponse("200 OK", [("Content-type", "image/x-icon")])
                return f
            except:
                return self._error(environ, _startResponse, 404)
            
        # Look up factory for current path and call it.
        path = environ["PATH_INFO"]
        for factory in self.factories:
            if factory.match(path):
                try:
                    return factory(environ, _startResponse)
                except Exception as err:
                    log.error(str(err), exc_info=True)
                    return self._error(environ, _startResponse, 500)
                break
        else:
            log.error("No factory found for %s" % path)
            return self._error(environ, _startResponse, 404)



