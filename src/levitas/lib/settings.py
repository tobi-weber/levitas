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
import traceback
import logging

from . import utils
from .singleton import Singleton


log = logging.getLogger("levitas.lib.SETTINGS")
     
     
class SettingMissing(Exception):
    pass


class Settings(Singleton):
    
    def __init__(self):
        log.info("Settings initialized")
        if "LEVITAS_SETTINGS" in os.environ:
            name = os.environ["LEVITAS_SETTINGS"]
        else:
            raise ImportError("Could not import SETTINGS: "
                              "os.environ[\"LEVITAS_SETTINGS\"] missing")
            
        try:
            __import__(name)
            SETTINGS = sys.modules[name]
        except ImportError as e:
            t = traceback.format_exc()
            error = """
            Could not import SETTINGS module '%s'
            (Is it on sys.path? Does it have syntax errors?)
            Error message: %s
            
            %s """ % (name, e, t)
            log.error(error)
            raise ImportError(error)
        except:
            utils.logTraceback()
            raise
            
        for setting in dir(SETTINGS):
            if not (setting.startswith("__") and setting.endswith("__")):
                setting_value = getattr(SETTINGS, setting)
                #log.debug("Set setting %s" % setting)
                setattr(self, setting, setting_value)

    def require(self, name, example=""):
        if not hasattr(self, name):
            msg = "You must define the '%s' in your SETTINGS module: %s" \
                    % (name, os.environ["LEVITAS_SETTINGS"])
            if example:
                msg += "\nExample: %s" % example
            raise SettingMissing(msg)
        