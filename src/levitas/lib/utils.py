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
import stat
import traceback
import time
import datetime
import email.utils
import posixpath
import mimetypes


def getTraceback():
    return traceback.format_exc()

    
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LOWER = []
for month in MONTHS:
    MONTHS_LOWER.append(month.lower())

    
def parse_http_datetime(s):
    return datetime.datetime(*email.utils.parsedate(s)[:6])


def time2netscape(t=None):
    """Return a string representing time in seconds since epoch, t.

    If the function is called without an argument, it will use the current
    time.

    The format of the returned string is like this:

    Wed, DD-Mon-YYYY HH:MM:SS GMT

    """
    if t is None:
        t = time.time()
    year, mon, mday, hour, min, sec, wday = time.gmtime(t)[:7]  # @ReservedAssignment
    return "%s, %02d-%s-%04d %02d:%02d:%02d GMT" % (
        DAYS[wday], mday, MONTHS[mon - 1], year, hour, min, sec)
 
 
def file_size(path):
    return os.stat(path)[stat.ST_SIZE]
    
 
def guess_type(path, custom_mimetypes=None):
    custom_mimetypes = custom_mimetypes or {}
    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()  # @UndefinedVariable
    extensions_map.update({
        "": "application/octet-stream",  # Default
        ".py": "text/plain",
        ".c": "text/plain",
        ".h": "text/plain",
        ".appcache": "text/cache-manifest",
        ".webapp": "application/x-web-app-manifest+json"
        })
    extensions_map.update(custom_mimetypes)
    base, ext = posixpath.splitext(path)  # @UnusedVariable
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map[""]
    
        
        