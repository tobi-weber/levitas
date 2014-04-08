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
import mimetypes
try:
    from urllib import unquote  # python 2
except ImportError:
    from urllib.parse import unquote  # python 3
import posixpath
import logging
import time
try:
    from cookielib import http2time  # python 2
except ImportError:
    from http.cookiejar import http2time  # python 3

from levitas.lib import utils

from .middleware import Middleware


log = logging.getLogger("levitas.middleware.fileMiddleware")


class FileMiddleware(Middleware):
    """
    Handles static files from a given path.
    
    Example settings entry:
    urls = [(r"^/(.*)", FileMiddleware, {"path": "/path/to/files"})]
    """
    
    LOG = True
    
    BLOCKSIZE = 4096
    
    MIMETYPES = {}
    
    DAY_SEC = 360 * 24 * 60 * 60
    
    CACHE = {".htm": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".html": {"max_age": DAY_SEC,
                       "must_revalidate": True
                      },
             ".ico": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".jpg": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".jpeg": {"max_age": DAY_SEC,
                       "must_revalidate": True
                      },
             ".png": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".gif": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".swf": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             ".js": {"max_age": DAY_SEC,
                     "must_revalidate": True
                    },
             ".css": {"max_age": DAY_SEC,
                      "must_revalidate": True
                     },
             }
    
    def __init__(self, path):
        """
        @param path: Path of files to serve
        """
        Middleware.__init__(self)
        os.chdir(path)
        log.debug("Working directory: %s" % os.getcwd())
        
        self.static_path = path
        """
        Path to the static files
        """
        self.ctype = ""
        """ The content-type of the file"""
        self.size = 0
        """ file-size """
        self.fpath = None
        """ absolute path of the file"""
        if hasattr(self.settings, "filecache"):
            self.cache = self.settings.filecache
        else:
            self.cache = FileMiddleware.CACHE
        
    def prepare(self):
        self.preparePath()
        self.prepareFile()
    
    def preparePath(self):
        """ set the path in the filesystem """
        self.fpath = self.translate_path(self.path, self.static_path)
    
    def prepareFile(self):
        """ set the content-type and the file-size """
        if self.fpath:
            self.ctype = self.guess_type(self.fpath)
            if os.path.exists(self.fpath):
                self.size = os.stat(self.fpath)[stat.ST_SIZE]
            else:
                self.size = 0
        
    def get(self):
        f = self.getFile(self.fpath)
        if f is None:
            return self.responseError(404)
        
        self.prepareCacheHeaders()
        
        if self.checkCacheInfo(self.fpath):
            self.response_code = 304
            return
        
        self.addHeader("Content-type", self.ctype)
         
        self.addHeader("Content-Length", str(self.size))

        return f
        
    def head(self):
        return self.get()
        
    def getFile(self, path):
        try:
            f = open(path, "r+b")
            return f
        except IOError as e:
            log.debug(str(e))
            return None
        
    def checkCacheInfo(self, path):
        try:
            mtime = self.get_mtime(path)
            if "HTTP_IF_MODIFIED_SINCE" in self.request_headers:
                if_modified_since = self.request_headers["HTTP_IF_MODIFIED_SINCE"]
                try:
                    if_modified_since = http2time(if_modified_since)
                except Exception as err:
                    log.error(err)
                    return False
                if int(mtime) > int(if_modified_since):
                    return False
                else:
                    return True
            else:
                return False
        except Exception as err:
            log.error(str(err), exc_info=True)
            return False
        
    def prepareCacheHeaders(self):
        ext = os.path.splitext(self.fpath)[1].lower()
        if ext in list(self.cache.keys()):
            self.setCacheHeaders(self.fpath, **self.cache[ext])
        else:
            self.setCacheHeaders(self.fpath)
        
    def setCacheHeaders(self, path, no_cache=False, no_store=False,
                        max_age=0, must_revalidate=False):
        t = self.get_mtime(path)
        last_modified = utils.time2netscape(t)
        self.addHeader("Last-Modified", last_modified)
        #expires = asctime(gmtime(time() + expires_secs))
        #self.addHeader("Expires", expires)
        
        cache_control = []
        if no_cache:
            cache_control.append("no-cache")
        if no_store:
            cache_control.append("no-store")
        if max_age:
            cache_control.append("max-age=%d" % max_age)
            #cache_control += ", s-max-age=%d" % max_age
        if must_revalidate:
            cache_control.append("must-revalidate")
            
        if not cache_control:
            cache_control.append("no-cache")
            cache_control.append("must-revalidate")
            #cache_control.append("no-store")
            
        self.addHeader("Cache-Control", ", ".join(cache_control))
        
    def get_mtime(self, path):
        try:
            mtime = os.path.getmtime(path)
        except Exception as err:
            log.error("Unable to get modification time of file %s" % path)
            log.error(str(err), exc_info=True)
            return time.time()
        
        return mtime
        
    def translate_path(self, path, cwd):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(unquote(path))
        words = path.split("/")
        words = [_f for _f in words if _f]
        path = cwd
        for word in words:
            drive, word = os.path.splitdrive(word)  # @UnusedVariable
            head, word = os.path.split(word)  # @UnusedVariable
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'

        return path
            
    def guess_type(self, path):
        base, ext = posixpath.splitext(path)  # @UnusedVariable
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map[""]

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
    extensions_map.update(MIMETYPES)
        
        
        