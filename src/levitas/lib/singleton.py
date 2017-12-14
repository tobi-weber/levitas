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

import os
import logging


log = logging.getLogger("levitas.lib.singleton")


class Singleton(object):
        
    def __new__(cls, *dt, **mp):
        if not hasattr(cls, "_inst"):
            cls._inst = super(Singleton, cls).__new__(cls)
        else:
            def init_pass(self, *dt, **mp):
                pass
            cls.__init__ = init_pass
            
        return cls._inst
    
    
class ProcessBork(object):
    """
    Handle a Singleton-Instance for every process/subprocess.
    The constructor must be called by the classmethod getInstance(*args, **kwargs)
    """
    
    @classmethod
    def getInstance(cls, *dt, **mp):
        pid = os.getpid()
        if not hasattr(cls, "_instances"):
            setattr(cls, "_instances", dict())
        if pid not in cls._instances:
            cls._instances[pid] = cls(*dt, **mp)
        else:
            pass
        return cls._instances[pid]
    