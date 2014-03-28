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
import sys
import time
import stat
import unittest
try:
    from urllib import request  # python 3
    from urllib.error import HTTPError
except ImportError:
    import urllib2 as request  # python 2
    from urllib2 import HTTPError

from levitas.middleware.middleware import Middleware
from tests import test
from .utf8_chars import UTF8_CHARS
try:
    import Cookie  # python 2
    import cookielib as cookiejar
except ImportError:
    import http.cookies as Cookie  # python 3
    from http import cookiejar

SETTINGS = \
"""
from tests.middleware_test import (Test_none_result,
                                   Test_empty_result,
                                   Test_empty_result_list,
                                   Test_response_string_py2,
                                   Test_response_string_py3,
                                   Test_response_bytes,
                                   Test_charset,
                                   Test_invalid_result,
                                   Test_addHeader,
                                   Test_response_error,
                                   Test_response_redirect,
                                   Test_redirected,
                                   Test_response_file,
                                   Test_get_browser_language,
                                   Test_get_cookie,
                                   Test_set_cookie,
                                   Test_clear_cookie,
                                   Test_set_signed_cookie,
                                   Test_get_signed_cookie,
                                   Test_get_args,
                                   Test_post_args,
                                   Test_post_fileupload)
                                   
cookie_secret = "mysecret"
                                   
urls = [
(r"^/none_result", Test_none_result),
(r"^/empty_result", Test_empty_result),
(r"^/empty_result_list", Test_empty_result_list),
(r"^/response_string_py2", Test_response_string_py2),
(r"^/response_string_py3", Test_response_string_py3),
(r"^/response_bytes", Test_response_bytes),
(r"^/charset", Test_charset),
(r"^/invalid_result", Test_invalid_result),
(r"^/addHeader", Test_addHeader),
(r"^/response_error", Test_response_error),
(r"^/response_redirect", Test_response_redirect),
(r"^/redirected", Test_redirected),
(r"^/response_file", Test_response_file),
(r"^/get_browser_language", Test_get_browser_language),
(r"^/get_cookie", Test_get_cookie),
(r"^/set_cookie", Test_set_cookie),
(r"^/clear_cookie", Test_clear_cookie),
(r"^/set_signed_cookie", Test_set_signed_cookie),
(r"^/get_signed_cookie", Test_get_signed_cookie),
(r"^/get_args", Test_get_args),
(r"^/post_args", Test_post_args),
(r"^/post_fileupload", Test_post_fileupload),
]
"""


class Test_none_result(Middleware):
    
    def get(self):
        return None


class Test_empty_result(Middleware):
    
    def get(self):
        return ""
    
    
class Test_empty_result_list(Middleware):
    
    def get(self):
        return []
    
    
class Test_charset(Middleware):
    
    def get(self):
        return UTF8_CHARS
    
    
class Test_invalid_result(Middleware):
    
    def get(self):
        class NotIterObj(object):
            pass
        
        return NotIterObj()
    
    
class Test_response_string_py2(Middleware):
    
    def get(self):
        if sys.version_info[0] == 3:
            return b"test string"
        else:
            return "test string"
    
    
class Test_response_string_py3(Middleware):
    
    def get(self):
        if sys.version_info[0] == 3:
            return "test string"
        else:
            return u"test string"
    
    
class Test_response_bytes(Middleware):
    
    def get(self):
        return b"test string"
    
    
class Test_response_encoded_string(Middleware):
    
    def get(self):
        if sys.version_info[0] == 3:
            return "test string".encode(self._encoding)
        else:
            return u"test string".encode(self._encoding)
    

class Test_addHeader(Middleware):
    
    def get(self):
        self.addHeader("Test-Header", "Test-Value")
        return
    
    
class Test_response_error(Middleware):
    
    def get(self):
        return self.response_error(600, "Test-Error")
    
    
class Test_response_file(Middleware):
    
    def get(self):
        f = "tests/testfile.png"
        s = os.stat(f)[stat.ST_SIZE]
        self.addHeader("Content-type", "image/png")
        self.addHeader("Content-Length", str(s))
        return open(f, "rb")
    
    
class Test_response_redirect(Middleware):
    
    def get(self):
        return self.response_redirect("/redirected")
    

class Test_redirected(Middleware):
    
    def get(self):
        return u"redirected"
    

class Test_get_browser_language(Middleware):

    def get(self):
        return u",".join(self.get_browser_language())
    

class Test_get_cookie(Middleware):

    def get(self):
        return self.get_cookie("testcookie", "get cookie error")
    

class Test_set_cookie(Middleware):

    def get(self):
        self.set_cookie("testcookie", "testvalue", expires_days=14, httponly=True)
        return
    

class Test_clear_cookie(Middleware):

    def get(self):
        self.clear_cookie("testcookie")
        return
    

class Test_set_signed_cookie(Middleware):

    def get(self):
        self.set_signed_cookie("testcookie", "testvalue", expires_days=14, httponly=True)
        return
    

class Test_get_signed_cookie(Middleware):

    def get(self):
        return self.get_signed_cookie("testcookie")
    

class Test_get_args(Middleware):
    
    def post(self):
        return []
    
    
class Test_post_args(Middleware):
    
    def post(self):
        return []
    
    
class Test_post_fileupload(Middleware):
    
    def post(self):
        return []
    
    
class MiddlewareTest(unittest.TestCase):
    
    def setUp(self):
        self.headers = {}
        self.opener = request.build_opener()
        self.url = "http://localhost:8987/"
        
    def _request(self, path, data=None):
        if data is not None:
            data = data.encode("utf-8")
        try:
            url = os.path.join(self.url, path)
            #print("Call url: %s" % url)
            req = request.Request(url,
                                  data=data,
                                  headers=self.headers)
            response = self.opener.open(req)
        except Exception as err:
            return err
        
        return response
    
    def test_handler_404(self):
        obj = self._request("some_path")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 404, type(obj))
    
    def test_none_result(self):
        obj = self._request("none_result")
        #info = obj.info()
        #code = obj.code
        data = obj.read()
        self.assertTrue(data == b"", data)
    
    def test_empty_result(self):
        obj = self._request("empty_result")
        data = obj.read()
        self.assertTrue(data == b"", data)
    
    def test_empty_result_list(self):
        obj = self._request("empty_result_list")
        data = obj.read()
        self.assertTrue(data == b"", data)
        
    def test_response_string_py2(self):
        obj = self._request("response_string_py2")
        self.assertTrue(obj.code == 200, type(obj))
        
    def test_response_string_py3(self):
        obj = self._request("response_string_py3")
        self.assertTrue(obj.code == 200, type(obj))
        
    def test_response_bytes(self):
        obj = self._request("response_bytes")
        self.assertTrue(obj.code == 200, type(obj))
    
    def test_charset(self):
        obj = self._request("charset")
        data = obj.read()
        s = data.decode("utf-8")
        self.assertTrue(s == UTF8_CHARS, s)
    
    def test_invalid_result(self):
        obj = self._request("invalid_result")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 500, type(obj))
    
    def test_addHeader(self):
        obj = self._request("addHeader")
        headers = obj.headers
        self.assertTrue(headers["Test-Header"] == "Test-Value", str(obj))
        
    def test_response_error(self):
        obj = self._request("response_error")
        self.assertTrue(obj.code == 600, str(obj))
    
    def test_response_file(self):
        obj = self._request("response_file")
        headers = obj.headers
        f = "tests/testfile.png"
        s = os.stat(f)[stat.ST_SIZE]
        self.assertTrue(headers["Content-type"] == "image/png", str(obj))
        self.assertTrue(headers["Content-Length"] == str(s), str(obj))
        
    def test_response_redirect(self):
        obj = self._request("response_redirect")
        self.assertTrue(obj.read() == b"redirected", str(obj))
    
    def test_get_browser_language(self):
        lang_header = "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3"
        self.headers["ACCEPT_LANGUAGE"] = lang_header
        obj = self._request("get_browser_language")
        self.assertTrue(obj.read() == b"de-de,de,en-us,en", str(obj))
        
    def test_get_cookie(self):
        self.headers["Cookie"] = "testcookie=testvalue"
        obj = self._request("get_cookie")
        data = obj.read()
        self.assertTrue(data == b"testvalue", data)
    
    def test_set_cookie(self):
        obj = self._request("set_cookie")
        info = obj.info()
        cookies = Cookie.BaseCookie()
        cookies.load(info["Set-Cookie"])
        self.assertTrue("testcookie" in cookies,
                        "'testcookie' in cookies")
        cookie = cookies["testcookie"]
        self.assertTrue(cookie["path"] == "/", cookie["path"])
        t = cookiejar.http2time(cookie["expires"])
        self.assertTrue(t >= time.time(),
                        "expires is smaller then current time")
        self.assertTrue("httponly" in cookie,
                        "'httponly' in cookie")
        
    def test_clear_cookie(self):
        self.headers["Cookie"] = "testcookie=testvalue"
        obj = self._request("clear_cookie")
        info = obj.info()
        cookies = Cookie.BaseCookie()
        cookies.load(info["Set-Cookie"])
        self.assertTrue("testcookie" in cookies,
                        "'testcookie' in cookies")
        cookie = cookies["testcookie"]
        t = cookiejar.http2time(cookie["expires"])
        self.assertTrue(t < time.time(),
                        "expires time must be smaller then current time")
    
    def test_signed_cookie(self):
        obj = self._request("set_signed_cookie")
        info = obj.info()
        cookies = Cookie.BaseCookie()
        cookies.load(info["Set-Cookie"])
        self.assertTrue("testcookie" in cookies,
                        "'testcookie' in cookies")
        cookie = cookies["testcookie"]
        self.headers["Cookie"] = cookie.OutputString()
        obj = self._request("get_signed_cookie")
        v = obj.read()
        self.assertEqual(v, b"testvalue", "get signed cookie must return 'testvalue'")
        
    
    """
    def test_get_args(self):
        obj = self._request("get_args")
        print(obj)
    
    def test_post_args(self):
        obj = self._request("post_args")
        print(obj)
    
    def test_post_fileupload(self):
        obj = self._request("post_fileupload")
        print(obj)
    """
   
        
def run():
    test.run(SETTINGS, "tests.middleware_test")


if __name__ == "__main__":
    run()
        
    