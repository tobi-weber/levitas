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
from .factory import MiddlewareFactory
from .middleware import Middleware
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
       
       # Log to syslog
       syslog = True
       syslog_verbose = True
       sysloghandler_kwargs = {"address": "/dev/log"}
    
    
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
       
    def __init__(self):
        log.debug("WSGIHandler created %d" % os.getpid())
        
        self.settings = Settings()
        
        if hasattr(self.settings, "syslog"):
            if self.settings.syslog:
                self._initSyslog()
        
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
        middleware_class = url[1]
        args = []
        kwargs = {}
        for p in url[2:]:
            if isinstance(p, (list, tuple)):
                args.extend(p)
            elif isinstance(p, dict):
                kwargs.update(p)
            else:
                args.append(p)
        log.debug("MiddlewareFactory: %s, %s, %s, %s" % (regex,
                                                         middleware_class.__name__,
                                                         str(args),
                                                         str(kwargs)))
        factory = MiddlewareFactory(regex, middleware_class, *args, **kwargs)
        self.factories.append(factory)
        
    def _error(self, environ, _startResponse, code):
        middleware = Middleware()
        middleware.initEnviron(environ, _startResponse)
        return middleware.responseError(code)
        
    def _initSyslog(self):
        from logging.handlers import SysLogHandler
        log = logging.getLogger()
        formatter = logging.Formatter("%(asctime)s - %(name)s "
                                  "- %(levelname)s - %(message)s")
        
        if hasattr(self.settings, "sysloghandler_kwargs"):
            kwargs = self.settings.sysloghandler_kwargs
        else:
            kwargs = {"address": "/dev/log"}
        handler = SysLogHandler(**kwargs)
        
        if hasattr(self.settings, "syslog_verbose"):
            if self.settings.syslog_verbose:
                log.setLevel(logging.DEBUG)
            else:
                log.setLevel(logging.INFO)
            
        handler.setFormatter(formatter)
        log.addHandler(handler)
        
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
        path = os.path.normpath(environ["PATH_INFO"])
        log.debug("Handling path %s" % path)
        for factory in self.factories:
            m = factory.match(path)
            if m is not None:
                try:
                    log.debug("Url match pattern: %s" % factory.pattern)
                    return factory(environ, _startResponse, m)
                except Exception as err:
                    log.error(str(err), exc_info=True)
                    return self._error(environ, _startResponse, 500)
                break
        else:
            log.error("No factory found for %s" % path, exc_info=True)
            return self._error(environ, _startResponse, 404)



