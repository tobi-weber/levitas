# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Tobias Weber <tobi-weber@gmx.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this FILE except in compliance with the License.
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

from tests import test
from .test import BaseTest
    
    
log = logging.getLogger("levitas.tests.dynSiteMiddlewareTest")


SETTINGS = \
"""
from levitas.middleware.dynSiteMiddleware import DynSiteMiddleware
from tests.dynSiteMiddlewareTest import TestSite
from tests.dynSiteMiddlewareTest import TestGroups

urls = [(r"^/testgroups/(\d{4})/(\d{2})/(\d{2})$", DynSiteMiddleware, TestGroups),
        (r"^/(.*)$", DynSiteMiddleware, TestSite),

]
"""


class TestSite(object):
    
    def index(self):
        return "Test"
    
    def test_arg(self, arg):
        return arg
            
    def testargs(self, *args):
        return ", ".join(args)


class TestGroups(object):
    
    def index(self, year, month, day):
        return "%s-%s-%s" % (year, month, day)


class DynSiteMiddlewareTest(BaseTest):
    
    def test_root(self):
        obj = self._request("/")
        self.assertEqual(obj.code, 200, "Test root failed: %s" % str(obj))
        data = obj.read()
        self.assertEqual(data, b"Test", "Test root failed: %s" % data)
        
    def test_index(self):
        obj = self._request("/index")
        self.assertEqual(obj.code, 200, "Test index failed: %s" % str(obj))
        data = obj.read()
        self.assertEqual(data, b"Test", "Test index failed: %s" % data)
        
    def test_positional_arg(self):
        obj = self._request("/test/arg/testarg")
        self.assertEqual(obj.code, 200, "Test positional arg failed: %s" % str(obj))
        data = obj.read()
        self.assertEqual(data, b"testarg", "Test positional arg failed: %s" % data)
        
    def test_positional_args(self):
        obj = self._request("/testargs/arg1/arg2")
        self.assertEqual(obj.code, 200, "Test positional args failed: %s" % str(obj))
        data = obj.read()
        self.assertEqual(data, b"arg1, arg2", "Test positional args failed: %s" % data)
        
    def test_groups(self):
        obj = self._request("/testgroups/2014/04/13")
        self.assertEqual(obj.code, 200, "Test groups failed: %s" % str(obj))
        data = obj.read()
        self.assertEqual(data, b"2014-04-13", "Test groups failed: %s" % data)
        
        
def run():
    return test.run(SETTINGS, DynSiteMiddlewareTest)


if __name__ == "__main__":
    run()
        