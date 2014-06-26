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

import re
import logging


log = logging.getLogger("levitas.factory")

   
class MiddlewareFactory(object):
    """
    Factory class for middleware classes.
    """
    
    def __init__(self, pattern, middleware_class,
                 *args, **kwargs):
        """
        @param pattern: Regular expression to be matched.
        @param middleware: middleware class to be invoked.
        @param kwargs: A dictionary of arguments to be passed
                       to the middleware"s contructor.
        """
        if not pattern.endswith("$"):
            pattern += "$"
        self.pattern = pattern
        self.regex = re.compile(pattern)
        self.middleware_class = middleware_class
        self.args = args
        self.kwargs = kwargs
        
    def match(self, path):
        log.debug("Test match %s" % self.pattern)
        return self.regex.match(path)
        
    def __call__(self, environ, start_response, re_match=None):
        middleware = self.middleware_class(*self.args, **self.kwargs)
        middleware.re_match = re_match
        log.debug("Url groups: %s" % str(re_match.groups()))
        log.debug("Load middleware %s" % str(self.middleware_class))
        return middleware(environ, start_response)
