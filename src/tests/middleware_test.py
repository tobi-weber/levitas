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
import unittest
import time
try:
    from urllib import request  # python 3
    from urllib.error import HTTPError
except ImportError:
    import urllib2 as request  # python 2
    from urllib2 import HTTPError

from levitas.middleware.middleware import Middleware
from tests import test

SETTINGS = \
"""
from tests.middleware_test import (Test_none_result,
                                   Test_empty_result,
                                   Test_empty_result_list,
                                   Test_invalid_result,
                                   Test_addHeader,
                                   Test_response_error,
                                   Test_response_redirect,
                                   Test_response_file,
                                   Test_get_browser_locale,
                                   Test_loadLanguage,
                                   Test_get_cookie,
                                   Test_set_cookie,
                                   Test_clear_cookie,
                                   Test_clear_all_cookies,
                                   Test_set_signed_cookie,
                                   Test_get_signed_cookie,
                                   Test_parse_http_datetime,
                                   Test_get_args,
                                   Test_post_args,
                                   Test_post_fileupload)
                                   
urls = [
(r"^/none_result", Test_none_result),
(r"^/empty_result", Test_empty_result),
(r"^/empty_result_list", Test_empty_result_list),
(r"^/invalid_result", Test_invalid_result),
(r"^/addHeader", Test_addHeader),
(r"^/response_erro", Test_response_error),
(r"^/response_redirect", Test_response_redirect),
(r"^/response_file", Test_response_file),
(r"^/get_browser_locale", Test_get_browser_locale),
(r"^/loadLanguag", Test_loadLanguage),
(r"^/get_cookie", Test_get_cookie),
(r"^/set_cookie", Test_set_cookie),
(r"^/clear_cookie", Test_clear_cookie),
(r"^/clear_all_cookie", Test_clear_all_cookies),
(r"^/set_signed_cookie", Test_set_signed_cookie),
(r"^/get_signed_cookie", Test_get_signed_cookie),
(r"^/parse_http_datetime", Test_parse_http_datetime),
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
    
    
class Test_invalid_result(Middleware):
    
    def get(self):
        class TestObj(object):
            pass
        
        return TestObj()
    

class Test_addHeader(Middleware):
    
    def get(self):
        self.addHeader("Test-Header", "Test-Value")
    
    
class Test_response_error(Middleware):
    
    def get(self):
        print("Test_response_error")
        return []
    
    
class Test_response_redirect(Middleware):
    
    def get(self):
        print("Test_response_redirect")
        return []
    
    
class Test_response_file(Middleware):
    
    def get(self):
        print("Test_response_file")
        return []
    

class Test_get_browser_locale(Middleware):

    def get(self):
        print("Test_get_browser_locale")
        return []
    

class Test_loadLanguage(Middleware):

    def get(self):
        print("Test_loadLanguage")
        return []
    

class Test_get_cookie(Middleware):

    def get(self):
        print("Test_get_cookie")
        return []
    

class Test_set_cookie(Middleware):

    def get(self):
        print("Test_set_cookie")
        return []
    

class Test_clear_cookie(Middleware):

    def get(self):
        print("Test_clear_cookie")
        return []
    

class Test_clear_all_cookies(Middleware):

    def get(self):
        print("Test_clear_all_cookies")
        return []
    

class Test_set_signed_cookie(Middleware):

    def get(self):
        print("Test_set_signed_cookie")
        return []
    

class Test_get_signed_cookie(Middleware):

    def get(self):
        print("Test_get_signed_cookie")
        return []
    

class Test_parse_http_datetime(Middleware):

    def get(self):
        print("Test_parse_http_datetime")
        return []
    

class Test_get_args(Middleware):
    
    def post(self):
        print("Test_get_args")
        return []
    
    
class Test_post_args(Middleware):
    
    def post(self):
        print("Test_post_args")
        return []
    
    
class Test_post_fileupload(Middleware):
    
    def post(self):
        print("Test_post_fileupload")
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
    
    def test_none_result(self):
        obj = self._request("none_result")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 500, str(obj))
    
    def test_empty_result(self):
        obj = self._request("empty_result")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 500, str(obj))
    
    def test_empty_result_list(self):
        obj = self._request("empty_result_list")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 500, str(obj))
    
    def test_invalid_result(self):
        obj = self._request("invalid_result")
        self.assertTrue(isinstance(obj, HTTPError) and \
                        obj.code == 500, str(obj))
    
    def test_addHeader(self):
        obj = self._request("addHeader")
        #print(obj)
    
    """
        
    def test_response_error(self):
        obj = self._request("response_error")
        print(obj)
    
    def test_response_file(self):
        obj = self._request("response_file")
        print(obj)
    
    def test_response_redirect(self):
        obj = self._request("response_redirect")
        print(obj)
    
    def test_get_browser_locale(self):
        obj = self._request("get_browser_locale")
        print(obj)
    
    def test_loadLanguage(self):
        obj = self._request("loadLanguage")
        print(obj)
    
    def test_get_cookie(self):
        obj = self._request("get_cookie")
        print(obj)
    
    def test_set_cookie(self):
        obj = self._request("set_cookie")
        print(obj)
    
    def test_clear_cookie(self):
        obj = self._request("clear_cookie")
        print(obj)
    
    def test_clear_all_cookies(self):
        obj = self._request("clear_all_cookies")
        print(obj)
    
    def test_set_signed_cookie(self):
        obj = self._request("set_signed_cookie")
        print(obj)
    
    def test_get_signed_cookie(self):
        obj = self._request("get_signed_cookie")
        print(obj)
    
    def test_parse_signed_cookie(self):
        obj = self._request("parse_signed_cookie")
        print(obj)
    
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
        
    