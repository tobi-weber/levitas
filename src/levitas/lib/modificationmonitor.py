# -*- coding: utf-8 -*-
# Copyright (C) 2015 Tobias Weber <tobi-weber@gmx.de>
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
import time
import subprocess
import logging
import fnmatch
import signal

from levitas.lib.settings import Settings


log = logging.getLogger("levitas.lib.modificationmonitor")


class ModificationMonitor:
                                                                                             
    _process = None
    """
    process ID of the subprocess
    """

    def __init__(self, root_directory=None, file_extensions=["py"]):
        """
        Monitoring and reloading file modifications.
        
        Example settings (optional):
            # Which directory is the root of the source files?
            # Default current working directory.
            modificationmonitor_root_directory = "/root/path"
            # Which files should be monitored for modification?
            # Default *.py files.
            modificationmonitor_file_extensions = ["py"]
            # How often should we check for changes (in seconds)?
            # Default one second.
            modificationmonitor_poll_interval = 1
        """
        settings = Settings()
        if hasattr(settings, "modificationmonitor_root_directory"):
            self._root_directory = settings.modificationmonitor_root_directory
        else:
            self._root_directory = os.getcwd()
        if hasattr(settings, "modificationmonitor_file_extensions"):
            extensions = settings.modificationmonitor_file_extensions
            self._file_patterns = [r"[!.]*.%s" % ext for ext in extensions]
        else:
            self._file_patterns = [r"[!.]*.py"]

            self._file_extensions = ["py"]
        if hasattr(settings, "modificationmonitor_poll_interval"):
            self._poll_interval = settings.modificationmonitor_poll_interval
        else:
            self._poll_interval = 1
        self.files = self.get_files()
        
        log.info("Root directory: %s" % self._root_directory)
        self.setsignals()
        self.start_program()
        while True:
            time.sleep(self._poll_interval)
            if self.poll():
                log.info("Noticed a change in program source. Restarting...")
                self.start_program()
    
    def setsignals(self):
        signal.signal(signal.SIGTERM, self.sigexit)
        signal.signal(signal.SIGHUP, self.sigexit)
        signal.signal(signal.SIGINT, self.sigexit)
        signal.signal(signal.SIGQUIT, self.sigexit)
        
    def sigexit(self, sig, frame):
        log.debug("Stop ModificationMonitor process")
        os.killpg(self._process.pid, signal.SIGTERM)
        self._process.wait()
        sys.exit(0)

    def get_files(self):
        """
        Get a list of all files along with their timestamps for last modified
        """
        files = []
        for root, dirnames, filenames in os.walk(self._root_directory):
            for file_pattern in self._file_patterns:
                for filename in fnmatch.filter(filenames, file_pattern):
                    full_filename = os.path.join(root, filename)
                    files.append(full_filename)
        
        # Attach the last modified dates
        files = map(lambda f: (f, os.stat(f).st_mtime), files)
        
        return files
    
    def poll(self):
        new_files = self.get_files()
        if self.files != new_files:
            self.files = new_files
            return True
        return False
    
    def start_program(self):
        log.info("Start ModificationMonitor process")
        if self._process != None:
            log.debug("Stopping process")
            os.killpg(self._process.pid, signal.SIGTERM)
            self._process.wait()
        
        args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ["MODIFICATIONMONITOR_STARTED"] = 'true'
        
        self._process = subprocess.Popen(args, env=new_environ, preexec_fn=os.setsid)
        log.debug("Process started")
        
        
        
        