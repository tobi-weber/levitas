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

import unittest
import time
try:
    from urllib import request  # python 3
except ImportError:
    import urllib2 as request  # python 2

from tests import server


class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.headers = {}
        self.opener = request.build_opener()
        self.url = "http://localhost:8987"
        
    def _request(self, path, data=None):
        try:
            if not path.startswith("/"):
                path = "/%s" % path
            url = self.url + path
            #print("Call url: %s" % url)
            req = request.Request(url,
                                  data=data,
                                  headers=self.headers)
            response = self.opener.open(req)
        except Exception as err:
            return err
        
        return response


def run(SETTINGS, test):
    server.init_settings(SETTINGS)
    srv = server.WSGIServerThread()
    srv.start()
    time.sleep(0.5)
    suite = unittest.TestLoader().loadTestsFromTestCase(test)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    srv.stop()
    
    return res
    