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
import base64
import time
import hashlib
import hmac
import logging
if sys.version_info[0] == 3:
    STR = str
else:
    STR = unicode
from levitas.lib.settings import Settings
from levitas.lib.singleton import Singleton


log = logging.getLogger("levitas.utils.secure_cookie")


class SecureCookie(Singleton):
    
    def __init__(self):
        self._settings = Settings()

        if hasattr(self._settings, "encoding"):
            self._encoding = self._settings.encoding
        else:
            self._encoding = "utf-8"
        try:
            self._secret = self._settings.cookie_secret
        except:
            log.warning("Missing cookie_secret in settings!")
            self._secret = u"levitas_cookie_secret"
        if isinstance(self._secret, STR):
            self._secret = self._secret.encode(self._encoding)
    
    def encode_value(self, name, value):
        timestamp = str(int(time.time()))
        if isinstance(timestamp, STR):
            timestamp = timestamp.encode(self._encoding)
        if isinstance(value, STR):
            value = value.encode(self._encoding)
        value = base64.b64encode(value)
        signature = self._signature(name, value, timestamp)
        if isinstance(signature, STR):
            signature = signature.encode(self._encoding)
            
        value = b"|".join([value,
                          timestamp,
                          signature])
        
        return value
    
    def decode_value(self, name, value):
        parts = value.split("|")
        if len(parts) != 3:
            return None
            
        signature = self._signature(name, parts[0], parts[1])
        if not self._compare_digest(parts[2], signature):
            log.warning("Invalid cookie signature %r", value)
            return None
        
        timestamp = int(parts[1])
        if timestamp < time.time() - 31 * 86400:
            log.warning("Expired cookie %r", value)
            return None
        try:
            value = base64.b64decode(parts[0])
        except:
            value = None
            
        return value
        
    def _signature(self, *parts):
        """ Create a cookie-signature """
        h = hmac.new(self._secret,
                     digestmod=hashlib.sha1)
        
        for part in parts:
            if isinstance(part, STR):
                part = part.encode(self._encoding)
            h.update(part)
            
        return h.hexdigest()
    
    def _compare_digest(self, a, b):
        if hasattr(hmac, 'compare_digest'):  # python 3.3
            return hmac.compare_digest(a, b)
        if len(a) != len(b):
            return False
        result = 0
        if isinstance(a[0], int):  # python3 byte strings
            for x, y in zip(a, b):
                result |= x ^ y
        else:  # python2
            for x, y in zip(a, b):
                result |= ord(x) ^ ord(y)
        return result == 0
        
        
        