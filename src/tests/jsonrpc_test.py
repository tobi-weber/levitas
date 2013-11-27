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

import unittest
from json import loads
try:
    from urllib import request  # python 3
except ImportError:
    import urllib2 as request  # python 2
    
from levitas.middleware.service import Service

from tests import test

SETTINGS = \
"""
from levitas.middleware.jsonMiddleware import JSONMiddleware
from tests.jsonrpc_test import TestService
urls = [
(r"^/json/runtest", JSONMiddleware, {"service_class": TestService})
]
"""
   
    
class TestService(Service):
    
    def getArg(self):
        return "OK"

    def setArgs(self, arg1, arg2, arg3):
        return "Args: %s, %s, %s" % (arg1, arg2, arg3)
    
    def setNamedArgs(self, arg1="arg1", arg2="arg2", arg3="arg3"):
        return "Args: %s, %s, %s" % (arg1, arg2, arg3)
    
    def umlaute(self, text):
        return text


class JSONRPCTest(unittest.TestCase):
        
    def setUp(self):
        self.headers = {"Content-type": "application/json-rpc"}
        self.opener = request.build_opener()
        self.url = "http://localhost:8987/json/runtest"
        
    def _request(self, data):
        print(data)
        try:
            req = request.Request(self.url,
                                             data=data.encode("utf-8"),
                                             headers=self.headers)
            response = self.opener.open(req)
        except Exception as err:
            return err
        
        try:
            return loads(response.read().decode("utf-8"))
        except:
            raise
        
    def test_missing_params(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"getArg"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "OK")
    
    def test_missing_id(self):
        data = '{"jsonrpc":"2.0", "method":"get"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_unknown_method(self):
        data = '{"jsonrpc":"2.0","id":"ID01", "method":"get_unknown_method"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32601)
        
    def test_missing_protocol(self):
        data = '{"id":"ID01", "method":"get"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_wrong_protocol(self):
        data = '{"jsonrpc":"1.0", "id":"ID01", "method":"get"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_parse_error(self):
        data = '{jsonrpc":"2.0","id":"ID01","method":"get"}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32603)
        
    def test_set_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2","arg3"]}' # @IgnorePep8
        obj = self._request(data)
        print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: arg1, arg2, arg3")
        
    def test_invalid_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2"]}' # @IgnorePep8
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))
        
    def test_set_named_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"1","arg2":"2","arg3":"3"}}' # @IgnorePep8
        obj = self._request(data)
        print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: 1, 2, 3", str(obj))
        
    def test_invalid_named_args(self):
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"arg1","arg2":"arg2","arg4":"arg3"}}' # @IgnorePep8
        obj = self._request(data)
        print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))
        
    def test_umlaute(self):
        data = u'{"jsonrpc":"2.0","id":"ID01","method":"umlaute","params":["äöüß"]}'
        obj = self._request(data)
        print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertTrue(obj["result"], u"aöüß")
        
        
def run():
    test.run(SETTINGS, "tests.jsonrpc_test")


if __name__ == "__main__":
    run()
