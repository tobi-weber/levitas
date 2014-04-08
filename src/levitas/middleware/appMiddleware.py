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

from .fileMiddleware import FileMiddleware


log = logging.getLogger("levitas.middleware.appMiddleware")


class AppMiddleware(FileMiddleware):
    """
    
    Example settings entry:
    urls = [(r"^/(.*)", AppMiddleware, {"path": "/var/www"})]
    """
    LOG = True
    #CACHE = {}
    
    def __init__(self, path, disable_http_caching=False):
        """
        @param path: Path of files to serve
        @param disable_http_caching:
        """
        FileMiddleware.__init__(self, path)
        if disable_http_caching:
            self.cache = {}
        
    def get(self):
        if os.path.isdir(self.fpath):
            if not self.path.endswith("/"):
                return self.redirect(self.path + "/")
            for index in "index.html", "index.htm":
                index = os.path.join(self.fpath, index)
                if os.path.exists(index):
                    self.fpath = index
                    self.prepareFile()
                    break
            else:
                return self.responseError(404)
        return self._responseFile()
    
    