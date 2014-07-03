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

from . import Middleware


log = logging.getLogger("levitas.middleware.dynSiteMiddleware")


class PostFile(object):
    
    def __init__(self, filename, f, mtype, mtype_options):
        self.filename = filename
        self.file = file
        self.type = mtype
        self.type_options = mtype_options
        

class DynSiteMiddleware(Middleware):
    """
    class MySite(object):
    
        def index(self):
            return "Hello World"
            
    
    Example settings entry:
    urls = [(r"^/(.*)$", DynSiteMiddleware, MySite)]
    """
    
    def __init__(self, dynsite_class,
                 dynsite_args=[],
                 dynsite_kwargs={}):
        Middleware.__init__(self)
        self._dynsite_class = dynsite_class
        self._dynsite_args = dynsite_args
        self._dynsite_kwargs = dynsite_kwargs
        
    def get(self):
        kwargs = {}
        if self.request_data is not None:
            for k, v in self.request_data.items():
                if len(v) == 1:
                    kwargs[k] = v[0]
                else:
                    kwargs[k] = v

        return self._callDynSite(kwargs)
    
    def post(self):
        kwargs = {}
        if self.request_data is not None:
            data = self.request_data
            for k in data.keys():
                d = data[k]
                if d.filename is None:
                    kwargs[k] = d.value
                else:
                    kwargs[d.name] = PostFile(d.filename,
                                              d.file,
                                              d.type,
                                              d.type_options)
                
        return self._callDynSite(kwargs)
        
    def _callDynSite(self, kwargs):
        comps = []
        for g in self.url_groups():
            comps.extend(g.split("/"))
        comps = [comp for comp in comps if comp]
        if not len(comps):
            comps.append("index")
        
        site = self._dynsite_class(*self._dynsite_args,
                                   **self._dynsite_kwargs)
        
        log.debug("Path components: %s" % ", ".join(comps))
        for i in range(len(comps) + 1):  # @UnusedVariable
            if i < len(comps):
                m = "_".join(comps[:i + 1])
                args = comps[i + 1:]
            else:
                m = "index"
                args = comps
            if hasattr(site, m):
                log.info("Call '%s' method '%s' with args '%s'"
                          % (self._dynsite_class.__name__,
                             m,
                             str(args)))
                try:
                    return getattr(site, m)(*args, **kwargs)
                except Exception as err:
                    log.error(str(err), exc_info=True)
                    return self.responseError(500, str(err))
        
        msg = "%s cannot handle args %s" % (self._dynsite_class.__name__,
                                            str(comps))
        log.error(msg)
        return self.responseError(404, msg)
        
        
        
        
        
    