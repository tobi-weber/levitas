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
import urllib
import cgi
import logging
from cStringIO import StringIO

from fileMiddleware import FileMiddleware


log = logging.getLogger("levitas.middleware.simpleHTTPMiddleware")


class SimpleHTTPMiddleware(FileMiddleware):
    """
    Same as pythons SimpleHTTPServer.
    Serves html from a given path.
    
    Example settings entry:
    urls = [(r"^/(.*)", SimpleHTTPMiddleware, {"path": "/var/www"})]
    """
    LOG = True
    
    def get(self):
        if os.path.isdir(self.fpath):
            if not self.path.endswith("/"):
                return self.response_redirect(self.path + "/")
            for index in "index.html", "index.htm":
                index = os.path.join(self.fpath, index)
                if os.path.exists(index):
                    self.fpath = index
                    self.prepareFile()
                    break
            else:
                f = self.list_directory(self.fpath)
                if isinstance(f, tuple):
                    return self.response_error(*f)
                else:
                    return self.response_file(f)
        return self.response_file()
        
    def list_directory(self, path):
        try:
            dirs = os.listdir(path)
        except os.error:
            return (404, "No permission for directory %s" % path)
        dirs.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in dirs:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            #linkname = linkname.encode(self._encoding)
            #displayname = displayname.encode(self._encoding)
            linkname = urllib.quote(linkname)
            displayname = cgi.escape(displayname)
            f.write('<li><a href="%s">%s</a>\n'
                    % (linkname, displayname))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        self.ctype = "text/html"  # set the content-type
        self.mode = "r"  # set the file-mode
        self.size = f.tell()  # set the file-size
        f.seek(0)
        return f
    
    
    
    
