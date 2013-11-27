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
try:
    from urllib import quote  # python 2
except ImportError:
    from urllib.parse import quote  # python 3
from io import BytesIO
from levitas import response_codes
from levitas.lib.settings import Settings


log = logging.getLogger("levitas.middleware.errorMiddleware")


DEFAULT_ERROR_MESSAGE = """\
<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code %(code)d.
<p>Message: %(message)s.
<p>Error code explanation: %(code)s = %(explain)s.
</body>
"""

DEFAULT_ERROR_CONTENT_TYPE = "text/html"


class ErrorMiddleware:
            
    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE
    
    def __init__(self, code, message=None):
        self.code = code
        self.message = message
        self.settings = Settings()
        if hasattr(self.settings, "encoding"):
            self._encoding = self.settings.encoding
        else:
            self._encoding = "utf-8"
        
    def response_error(self):
        try:
            short, l = response_codes[self.code]
        except KeyError:
            short, l = "???", "???"
        if self.message is None:
            self.message = short
        explain = l
        log.error("code %d, message: %s", self.code, self.message)
        content = (self.error_message_format %
                   {"code": self.code,
                    "message": quote(self.message),
                    "explain": explain})
        f = BytesIO()
        f.write(content.encode(self._encoding))
        size = f.tell()
        f.seek(0)
        headers = [("Content-Type", self.error_content_type)]
        status = "%s %s" % (str(self.code), short)
        self.start_response(status, headers)
        method = self.environ["REQUEST_METHOD"].lower()
        if method != "head" and self.code >= 200 and self.code not in (204, 304):
            headers.append(("Content-Length", str(size)))
            return f
        else:
            headers.append(("Content-Length", "0"))
            return []
        
    def __call__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        return self.response_error()
