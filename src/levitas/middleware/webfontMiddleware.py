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
from io import StringIO
from http.client import HTTPConnection

from .middleware import Middleware


log = logging.getLogger("levitas.middleware.webfontMiddleware")

global FONT_CACHE
FONT_CACHE = {}


class WebfontMiddleware(Middleware):
    """
    WebfontMiddleware pipes webfonts from external servers to
    the client.
    
    Example settings entry:
    urls =
    [(r"^/webfont/(.*)$", WebfontMiddleware,
     {"Ubuntu":
     "http://themes.googleusercontent.com/font?kit=_xyN3apAT_yRRDeqB3sPRg",
     "UbuntuBold":
     "http://themes.googleusercontent.com/font?kit=0ihfXUL2emPh0ROJezvraD8E0i7KZn-EPnyo3HZu7kw"}  # @IgnorePep8
    )]
    """
    LOG = True
    
    def __init__(self, webfonts={}):
        """
        @param webfonts: Mapping between names and external webfont urls.
        """
        Middleware.__init__(self)
        
        self.webfonts = {}
        for name, webfont_url in webfonts.items():
            self.webfonts[name] = Webfont(webfont_url)
        
    def get(self):
        parts = self.path.split("/")
        name = parts[len(parts) - 1]
        if name in self.webfonts:
            font, content_type = self.webfonts[name].get()
            f = StringIO()
            f.write(font)
            self.response_code = 200
            size = f.tell()
            f.seek(0)
            self.addHeader("Content-type", content_type)
            self.addHeader("Content-Length", str(size))
            #self.addHeader("Cache-Control", "no-cache")
            self.start_response()
            return f
        else:
            self.response_error(404, "Webfont %s not registered in middleware" % name)


class Webfont:
    
    def __init__(self, webfont_url):
        self.webfont_url = webfont_url
        
        http_parts = webfont_url.split("http://")
        url = http_parts[len(http_parts) - 1]
        url_parts = url.split("/")
        self.webfont_server = url_parts.pop(0)
        self.webfont_path = "/" + "/".join(url_parts)
        
        log.debug("Webfont Server: %s" % self.webfont_server)
        log.debug("Webfont Path: %s" % self.webfont_path)
        
    def get(self):
        global FONT_CACHE
        if self.webfont_url in FONT_CACHE:
            log.debug("Webfont loaded from cache")
            return FONT_CACHE[self.webfont_url]
        
        conn = HTTPConnection(self.webfont_server)
        conn.request("GET", self.webfont_path)
        response = conn.getresponse()
        log.debug("Webfont response: %s, %s" % (response.status, response.reason))
        log.debug( str(response.getheaders()) )
        content_type = response.getheader("Content-type")
        font = response.read()
        conn.close()
        
        FONT_CACHE[self.webfont_url] = (font, content_type)
        
        return font, content_type
        
        