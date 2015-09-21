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
import cgi
import logging

from .settings import Settings


log = logging.getLogger("levitas.lib.levitasFieldStorage")


class LevitasFieldStorage(cgi.FieldStorage):
    """
    Example settings
    ================
        # Path for uploaded files
        upload_path = "/path/to/upload/files"
    """
     
    def make_file(self, binary=None):
        settings = Settings()
        if hasattr(settings, "upload_path"):
            log.debug("Upload-Path: %s" % settings.upload_path)
            upload_path = settings.upload_path
        else:
            upload_path = None
        log.debug("Handling Fileupload")
        if upload_path:
            if not os.path.exists(upload_path):
                log.debug("Create upload_path %s" % upload_path)
                os.mkdir(upload_path)
            # strip leading path from f name to avoid directory traversal attacks
            filename = os.path.basename(self.filename)
            filepath = os.path.join(upload_path, filename)
            log.debug("Create filepath %s" % filepath)
            f = open(filepath, "w+b")
            return f
        else:
            import tempfile
            log.debug("Create Tempfile")
            return tempfile.TemporaryFile(mode="w+b")
