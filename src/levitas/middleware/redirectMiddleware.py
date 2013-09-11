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

from middleware import Middleware


log = logging.getLogger("levitas.middleware.redirectMiddleware")


class RedirectMiddleware(Middleware):
    """
    Redirects the client to the given URL for all GET requests.
    
    Example settings entry:
    urls = [(r"/oldpath", RedirectMiddleware,
            {"url": "/newpath", "permanent": True})]
    """
    LOG = True
    
    def __init__(self, url, permanent=True):
        """
        @param url: Redirect URL
        @param permanent:
        """
        Middleware.__init__(self)
        
        self._url = url
        self._permanent = permanent

    def get(self):
        return self.response_redirect(self._url, permanent=self._permanent)
