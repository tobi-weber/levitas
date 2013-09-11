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

import sys
import os
import imp
import time
import urllib2
import unittest
import logging
from wsgiref.simple_server import make_server
from json import loads
from threading import Thread

from levitas.handler import WSGIHandler


class LevitasTest(unittest.TestCase):
        
    from levitas.middleware.service import Service
    
    class TestService(Service):
        
        def getArg(self):
            return "OK"
    
        def setArgs(self, arg1, arg2, arg3):
            return "Args: %s, %s, %s" % (arg1, arg2, arg3)
        
        def setNamedArgs(self, arg1="arg1", arg2="arg2", arg3="arg3"):
            return "Args: %s, %s, %s" % (arg1, arg2, arg3)
            
    settings = \
"""
from levitas.middleware.jsonMiddleware import JSONMiddleware
from test import LevitasTest
urls = [
(r"^/json/test", JSONMiddleware, {"service_class": LevitasTest.TestService})
]
"""
        
    def setUp(self):
        def runserver():
            httpd = make_server("localhost", 8987, WSGIHandler())
            httpd.handle_request()
        module = imp.new_module("settings")
        exec self.settings in module.__dict__
        sys.modules["settings"] = module
        os.environ["LEVITAS_SETTINGS"] = "settings"
        Thread(target=runserver).start()
        time.sleep(1)
        self.headers = {"Content-type": "application/json-rpc"}
        self.opener = urllib2.build_opener()
        self.url = "http://localhost:8987/json/test"
        
    def _request(self, data):
        print data
        try:
            request = urllib2.Request(self.url, data=data, headers=self.headers)
            response = self.opener.open(request)
        except Exception, err:
            return err
        
        try:
            return loads(response.read())
        except:
            raise
    
    def test_missing_params(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"getArg"}'
        obj = self._request(data)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "OK")
        
    def test_missing_id(self):
        data = '{"jsonrpc":"2.0", "method":"get"}'
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_unknown_method(self):
        data = '{"jsonrpc":"2.0","id":"ID01", "method":"get_result"}'
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32601)
        
    def test_missing_protocol(self):
        data = '{"id":"ID01", "method":"get"}'
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_wrong_protocol(self):
        data = '{"jsonrpc":"1.0", "id":"ID01", "method":"get"}'
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_parse_error(self):
        data = '{jsonrpc":"2.0","id":"ID01","method":"get"}'
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32603)
        
    def test_set_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2","arg3"]}' # @IgnorePep8
        obj = self._request(data)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: arg1, arg2, arg3")
        
    def test_invalid_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2"]}' # @IgnorePep8
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))
        
    def test_set_named_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"1","arg2":"2","arg3":"3"}}' # @IgnorePep8
        obj = self._request(data)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: 1, 2, 3", str(obj))
        
    def test_invalid_named_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"arg1","arg2":"arg2","arg4":"arg3"}}' # @IgnorePep8
        obj = self._request(data)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))


if __name__ == "__main__":
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    unittest.main()
    
    