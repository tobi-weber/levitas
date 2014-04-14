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

import logging

from .middleware import Middleware


log = logging.getLogger("levitas.middleware.loggerMiddleware")


class LoggerMiddleware(Middleware):
    """
    Handles logging from python http-logging-handler.
    
    Example settings entry:
    urls = [(r"^/logging$", LoggerMiddleware, "myapp")]
    """
    LOG = False
    
    def __init__(self, loggerName=""):
        """
        @param loggerName: Name displayed in log.
        """
        Middleware.__init__(self)
        
        self.loggerName = loggerName
        
    def get(self):
        return self._do_logging(self.request_data)
    
    def post(self):
        return self._do_logging(self.request_data)
    
    def _do_logging(self, data):
        name = self.request_data["name"][0]
        name = self.loggerName + "." + name
        log = logging.getLogger(name)
        level = self.request_data["levelname"][0].upper()
        level = logging._levelNames[level]
        msg = self.request_data["msg"][0]
        msg += " - %s - %s" % (self.remote_host, self.request_headers["HTTP_USER_AGENT"])
        log.log(level, msg)
        
        return
        
        