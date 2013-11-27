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
import signal
import abc
import logging
from time import sleep
from multiprocessing import Process
from optparse import OptionParser

from .SETTINGS import SettingMissing


log = logging.getLogger("levitas.lib.daemonize")


def cli(daemon_class, daemon_args=[], daemon_kwargs={},
               chdir="/", umask=0):
    """
    Command-line interface to control a daemon.
    
    @param daemon_class: Subclass of L{AbstractDaemon}.
    @param daemon_args: Arguments to instantiate the daemon.
    @param daemon_kwargs: Named arguments to instantiate the daemon.
    @param chdir: Working directory of the daemon.
    @param umask: file mode creation mask.
    """
    name = os.path.basename(sys.argv[0])
    
    options = CLIOptions(name)
    try:
        options.parse_args()
    except CLIOptionError as err:
        sys.stderr.write(str(err))
        sys.exit(1)
    
    sys.stdout.write("%s %s: " % (options.action or "start", name))
    try:
        dz = Daemonizer(daemon_class,
                        chdir=chdir,
                        umask=umask,
                        daemon_args=daemon_args,
                        daemon_kwargs=daemon_kwargs)
        if dz.do_action(options.action, options.pidfile):
            sys.stdout.write("done\n")
            return True
        else:
            sys.stdout.write("failed\n")
            return False
    except SettingMissing as err:
        sys.stderr.write(err)


class AbstractDaemon(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self):
        pass
    
    @abc.abstractmethod
    def stop(self):
        pass
    

class Daemonizer(Process):
    
    def __init__(self, daemon_class,
                 chdir="/", umask=0,
                 daemon_args=[], daemon_kwargs={}):
        if not issubclass(daemon_class, AbstractDaemon):
            raise TypeError("%s is not subclass of %s"
                            % (str(daemon_class), str(AbstractDaemon)))
        Process.__init__(self)
        self.daemon_class = daemon_class
        self.chdir = chdir
        self.umask = umask
        self.daemon_args = daemon_args
        self.daemon_kwargs = daemon_kwargs
        self.pidfile = None
        self.daemon_process = None
        self._daemonize = False
    
    def read_pidfile(self):
        try:
            f = file(self.pidfile, "r")
            pid = int(f.read().strip())
            f.close()
        except IOError:
            pid = None
        return pid
            
    def do_action(self, action, pidfile):
        if not action in ["start", "stop", "restart", "foreground"]:
            action = "foreground"
            return
        
        self.pidfile = pidfile
        
        if pidfile is not None:
            pid = self.read_pidfile()
        else:
            pid = None
        
        if action == "start":
            return self.do_start_action(pid)
        elif action == "stop":
            return self.do_stop_action(pid)
        elif action == "restart":
            if self.do_stop_action(pid):
                pid = self.read_pidfile()
                return self.do_start_action(pid)
            else:
                return False
        elif action == "foreground":
            # Start as a subprocess without making a daemon
            self.start()
            return True
    
    def do_start_action(self, pid):
        if pid:
            msg = "Start aborted, pid-file '%s' exist.\n"
            sys.stderr.write(msg % self.pidfile)
            return False
        self._daemonize = True
        self.start()
        return True
    
    def do_stop_action(self, pid):
        if not pid:
            msg = "Could not stop process, missing pid-file '%s'.\n"
            sys.stderr.write(msg % self.pidfile)
            return False
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                sleep(0.1)
        except OSError:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
        return True
    
    def setsignals(self):
        signal.signal(signal.SIGTERM, self.sigexit)
        signal.signal(signal.SIGHUP, self.sigexit)
        signal.signal(signal.SIGINT, self.sigexit)
        signal.signal(signal.SIGQUIT, self.sigexit)
        
    def sigexit(self, sig, frame):
        self.daemon_process.stop()
        sys.exit(0)

    def run(self):
        # Make a daemon
        if self._daemonize:
            self.daemonize()
        try:
            self.start_daemon()
        except:
            raise
        
    def start_daemon(self):
        self.setsignals()
        os.chdir(self.chdir)
        self.daemon_process = self.daemon_class(*self.daemon_args,
                                   **self.daemon_kwargs)
        self.daemon_process.start()
        
    def daemonize(self):
        pid = os.fork()
        if pid != 0:
            # Parent
            os._exit(0)
        
        # Child
        os.close(0)
        sys.stdin = sys.__stdin__ = open("/dev/null")
        os.chdir(self.chdir)
        os.umask(self.umask)
        os.setsid()
        
        pid = str(os.getpid())
        if self.pidfile:
            f = file(self.pidfile, "w+")
            f.write("%s\n" % pid)
            f.close()


class CLIOptionError(Exception):
    pass


class CLIOptions(object):
    
    def __init__(self, name, custom_actions=None):
        self.name = name
            
        if custom_actions is None:
            self.actions = ["start", "stop", "restart", "foreground"]
        else:
            self.actions = custom_actions
        
        self.usage = "Usage: %s [OPTION]" % sys.argv[0]
        for i in range(len(self.actions)):
            if i == 0:
                self.usage += " {"
            else:
                self.usage += "|"
                
            self.usage += self.actions[i]
            
            if i == len(self.actions) - 1:
                self.usage += "}"
        
        self.parser = OptionParser(self.usage)
        
        self.options = None
        self.pidfile = None
        self.action = None
        
        self.addOption("-l", "--logfile",
                       dest="logfile",
                       help="Path to logfile (optional)")
        self.addOption("-c", "--logfilecount",
                       dest="logfilecount",
                       type="int", default=0,
                       help="Count of old logfiles to be saved. (default: 0)")
        self.addOption("-v", "--verbose",
                       dest="verbose",
                       action="store_true")
        self.addOption("-s", "--SETTINGS",
                       dest="settings_module",
                       help="SETTINGS module (required)",
                       metavar="SETTINGS_MODULE")
        self.addOption("-p", "--pidfile",
                       dest="pidfile",
                       default="/var/run/%s.pid" % self.name,
                       help="pidfile")
        
    def addOption(self, short, full, **kwargs):
        self.parser.add_option(short, full, **kwargs)
        
    def parse_args(self):
        options, args = self.parser.parse_args()
        
        self.options = options
            
        if len(args) == 1:
            if args[0] in self.actions:
                self.action = args[0]
        elif not self.action and len(self.actions) > 0:
            self.parser.print_help()
            raise CLIOptionError(self.usage)
        
        logfile = None
        logfilecount = 0
        
        if hasattr(options, "logfile"):
            logfile = options.logfile
            
        if hasattr(options, "logfilecount"):
            logfilecount = options.logfilecount
        
        if hasattr(options, "pidfile"):
            self.pidfile = options.pidfile
        
        if hasattr(options, "settings_module"):
            if options.settings_module:
                os.environ["LEVITAS_SETTINGS"] = options.settings_module
            else:
                self.parser.print_help()
                raise CLIOptionError("option --SETTINGS required")
        
        if self.action in ["start", "foreground"]:
            self._initLogging(options.verbose, logfile, logfilecount)
            
    def _initLogging(self, verbose=False, logfile=None, logfilecount=0):
        log = logging.getLogger()
        formatter = logging.Formatter("%(asctime)s - %(name)s "
                                      "- %(levelname)s - %(message)s")
        
        if logfile is None:
            h = logging.StreamHandler()
        else:
            from logging.handlers import TimedRotatingFileHandler
            h = TimedRotatingFileHandler(logfile, when="midnight", backupCount=logfilecount)
            h.doRollover()
            
        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            
        h.setFormatter(formatter)
        log.addHandler(h)
            
            