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


class Service(object):
    """
    Base class for JSONServices
    """
    
    def __init__(self, middleware, **kwargs):
        """
        @param middleware: Object of type L{JSONMiddleware}
        """
        self.middleware = middleware
        self._init(**kwargs)
    
    def _init(self, **kwargs):
        """
        Sets all kwargs to the service object.
        
        May be overridden.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        
    def _prepare(self):
        """
        Method will be called after service class is instantiated.
        
        May be overridden.
        """
        pass
    
    def _complete(self):
        """
        Method will be called after service method is finished.
        
        May be overridden.
        """
        pass
    