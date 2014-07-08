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
try:
    from urllib import urlencode  # python 2
except ImportError:
    from urllib.parse import urlencode  # python 3

from tests import test
from .test import BaseTest


log = logging.getLogger("levitas.tests.loggerMiddlewareTest")


SETTINGS = \
"""
from levitas.middleware.loggerMiddleware import LoggerMiddleware

urls = [(r"^/logging$", LoggerMiddleware, "levitas")]
"""
    

class LoggerMiddlewareTest(BaseTest):
    
    def test_get_logger(self):
        """Test logging get request"""
        params = {"name": "test",
                  "levelname": "info",
                  "msg": "loggerMiddleware get test"}
        path = "logging?%s" % urlencode(params, doseq=True)
        obj = self._request(path)
        self.assertEqual(obj.code, 200, "Remote logging get failed")
    
    def test_post_logger(self):
        """Test logging post request"""
        params = {"name": "test",
                  "levelname": "info",
                  "msg": "loggerMiddleware post test"}
        data = urlencode(params, doseq=True)
        obj = self._request("logging", data.encode("utf-8"))
        self.assertEqual(obj.code, 200, "Remote logging post failed")
        
    
def run():
    return test.run(SETTINGS, LoggerMiddlewareTest)


if __name__ == "__main__":
    run()
        
        
        
    