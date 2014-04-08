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

from tests import test
from .test import BaseTest


log = logging.getLogger("levitas.tests.loggerMiddlewareTest")


SETTINGS = \
"""
from levitas.middleware.appMiddleware import AppMiddleware

urls = [(r"^/(.*)$", AppMiddleware, {"path":
            "/home/tobi/Workspaces/Public/levitas/src/tests/files"})
]
"""
    

class AppMiddlewareTest(BaseTest):
    
    def test_index_html(self):
        obj = self._request("/")
        self.assertEqual(obj.code, 200, "Get index.html failed")
        
    
def run():
    return test.run(SETTINGS, AppMiddlewareTest)


if __name__ == "__main__":
    run()
        
        
        
    
    