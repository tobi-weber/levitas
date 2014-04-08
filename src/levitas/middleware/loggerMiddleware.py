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

from .middleware import Middleware


log = logging.getLogger("levitas.middleware.loggerMiddleware")


class LoggerMiddleware(Middleware):
    """
    Handles logging from python http-logging-handler.
    
    Example settings entry:
    urls = [(r"^/logging$", LoggerMiddleware, {"loggerName": "myapp"})]
    """
    LOG = False
    
    def __init__(self, loggerName="myapp"):
        """
        @param loggerName: Name displayed in log.
        """
        Middleware.__init__(self)
        
        self.loggerName = loggerName
    
    def post(self):
        name = self.request_data["name"][0]
        name = self.loggerName + "." + name
        log = logging.getLogger(name)
        level = self.request_data["levelname"][0]
        level = logging._levelNames[level]
        msg = self.request_data["msg"][0]
        if "args" in self.request_data:
            args = self.request_data["args"][0]
            msg = msg % args
        msg += " - %s - %s" % (self.remote_host, self.request_headers["HTTP_USER_AGENT"])
        log.log(level, msg)
        result = "logged"
        self.addHeader("Content-Length", str(len(result)))
        self.addHeader("Content-type", "text/plain; charset=utf-8")
        self.start_response()
        return result
        