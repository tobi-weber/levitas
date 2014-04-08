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

import os
import time
import stat
import logging

from tests import test
from .test import BaseTest


log = logging.getLogger("levitas.tests.fileMiddlewareTest")


SETTINGS = \
"""
from levitas.middleware.fileMiddleware import FileMiddleware

urls = [
(r"^/(.*)$", FileMiddleware, {"path":
            "/home/tobi/Workspaces/Public/levitas/src/tests/files"})
]
"""
    

class FileMiddlewareTest(BaseTest):
    
    def test_get_file(self):
        obj = self._request("testfile.png")
        headers = obj.headers
        f = "testfile.png"
        s = os.stat(f)[stat.ST_SIZE]
        self.assertTrue(headers["Content-type"] == "image/png", str(obj))
        self.assertTrue(headers["Content-Length"] == str(s), str(obj))
        
    def test_file_types(self):
        obj = self._request("test.html")
        info = obj.info()
        t = info["Content-type"]
        print(t)
        self.assertEqual(t, "text/html", "Content type must be text/html")
        obj = self._request("test.js")
        info = obj.info()
        t = info["Content-type"]
        print(t)
        self.assertEqual(t, "application/javascript",
                         "Content type must be application/javascript")
        obj = self._request("test.css")
        info = obj.info()
        t = info["Content-type"]
        print(t)
        self.assertEqual(t, "text/css", "Content type must be text/css")
        obj = self._request("test.png")
        info = obj.info()
        t = info["Content-type"]
        print(t)
        self.assertEqual(t, "image/png", "Content type must be image/png")
        obj = self._request("test.jpg")
        info = obj.info()
        t = info["Content-type"]
        print(t)
        self.assertEqual(t, "image/jpeg", "Content type must be image/jpeg")
        
    def test_cache_headers(self):
        f = open("tests/files/cachetest.html", "w")
        f.write("<html>TEST</html>")
        f.close()
        
        obj = self._request("cachetest.html")
        info = obj.info()
        
        self.headers["IF_MODIFIED_SINCE"] = info["Last-Modified"]
        obj = self._request("cachetest.html")
        self.assertEqual(obj.code, 304,
                         "Revalidate modification time failed. "
                         "Server did not return 304")
        
        time.sleep(1)
        f = open("cachetest.html", "w")
        f.write("<html>TEST2</html>")
        f.close()
        self.headers["IF_MODIFIED_SINCE"] = info["Last-Modified"]
        obj = self._request("cachetest.html")
        self.assertEqual(obj.code, 200,
                         "Revalidate modification time failed. "
                         "Server did not return 200")
        os.remove("cachetest.html")
        
    
def run():
    return test.run(SETTINGS, FileMiddlewareTest)


if __name__ == "__main__":
    run()
        
    
