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

from json import loads
import logging
    
from levitas.middlewares.service import Service

from tests import test
from .test import BaseTest
from .utf8_chars import UTF8_CHARS
    
log = logging.getLogger("levitas.tests.jsonrpc_test")


SETTINGS = \
"""
from levitas.middlewares.jsonMiddleware import JSONMiddleware
from tests.jsonMiddlewareTest import TestService
urls = [
(r"^/json/runtest$", JSONMiddleware, TestService)
]
"""
   
    
class TestService(Service):
    
    def getArg(self):
        return "OK"

    def setArgs(self, arg1, arg2, arg3):
        return "Args: %s, %s, %s" % (arg1, arg2, arg3)
    
    def setNamedArgs(self, arg1="arg1", arg2="arg2", arg3="arg3"):
        return "Args: %s, %s, %s" % (arg1, arg2, arg3)
    
    def utf8(self, text):
        return text


class JsonMiddlewareTest(BaseTest):
        
    def _request_json(self, data):
        self.headers["Content-type"] = "application/json-rpc"
        data = data.encode("utf-8")
        path = "json/runtest"
        response = self._request(path, data)
        try:
            return loads(response.read().decode("utf-8"))
        except:
            raise
        
    def test_missing_params(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01","method":"getArg"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "OK")
    
    def test_missing_id(self):
        print("")
        data = '{"jsonrpc":"2.0", "method":"get"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_unknown_method(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01", "method":"get_unknown_method"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32601)
        
    def test_missing_protocol(self):
        print("")
        data = '{"id":"ID01", "method":"get"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_wrong_protocol(self):
        print("")
        data = '{"jsonrpc":"1.0", "id":"ID01", "method":"get"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32600)
        
    def test_parse_error(self):
        print("")
        data = '{jsonrpc":"2.0","id":"ID01","method":"get"}'
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32603)
        
    def test_set_args(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2","arg3"]}' # @IgnorePep8
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: arg1, arg2, arg3")
        
    def test_invalid_args(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":["arg1","arg2"]}' # @IgnorePep8
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))
        
    def test_set_named_args(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"1","arg2":"2","arg3":"3"}}' # @IgnorePep8
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], "Args: 1, 2, 3", str(obj))
        
    def test_invalid_named_args(self):
        print("")
        data = '{"jsonrpc":"2.0","id":"ID01","method":"setArgs","params":{"arg1":"arg1","arg2":"arg2","arg4":"arg3"}}' # @IgnorePep8
        obj = self._request_json(data)
        #print(obj)
        self.assertTrue("error" in obj, str(obj))
        self.assertEqual(obj["error"]["code"], -32602, str(obj))
        
    def test_utf8(self):
        print("")
        data = u'{"jsonrpc":"2.0","id":"ID01","method":"utf8","params":["%s"]}' \
                % UTF8_CHARS.replace('"', '\\"')
        obj = self._request_json(data)
        #print(obj["result"])
        self.assertTrue("result" in obj, str(obj))
        self.assertEqual(obj["result"], UTF8_CHARS)
        
        
def run():
    return test.run(SETTINGS, JsonMiddlewareTest)


if __name__ == "__main__":
    run()
