# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Tobias Weber <tobi-weber@gmx.de>
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
from argparse import ArgumentParser

from levitas.lib.modificationmonitor import ModificationMonitor
from .settings import SettingMissing


log = logging.getLogger("levitas.lib.daemonize")


def cli(daemon_class, daemon_args=[], daemon_kwargs={}, umask=0):
    """
    Command-line interface to control a daemon.
    
    @param daemon_class: Subclass of L{AbstractDaemon}.
    @param daemon_args: Arguments to instantiate the daemon.
    @param daemon_kwargs: Named arguments to instantiate the daemon.
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
    
    if options.reloader and "MODIFICATIONMONITOR_STARTED" not in os.environ:
        sys.stdout.write("Start ModificationMonitor\n")
        ModificationMonitor()
        sys.exit(0)
    
    try:
        dz = Daemonizer(daemon_class,
                        chdir=os.getcwd(),
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


class AbstractDaemon:
    
    metaclass = abc.ABCMeta
    
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
            f = open(self.pidfile, "r")
            pid = int(f.read().strip())
            f.close()
        except IOError:
            pid = None
        return pid
            
    def do_action(self, action, pidfile):
        if action not in ["start", "stop", "restart", "foreground"]:
            action = "foreground"
        
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
        log.debug("Stop process")
        self.daemon_process.stop()
        sys.exit(0)

    def run(self):
        # Make a daemon
        if self._daemonize:
            self.daemonize()
        try:
            self.start_process()
        except:
            raise
        
    def start_process(self):
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
    
    def __init__(self, name):
        self.name = name
        
        self.parser = ArgumentParser()
        
        self.pidfile = None
        self.action = None
        
        self.parser.add_argument("action", type=str, nargs='?',
                                 choices=["start", "stop", "restart", "foreground"])
        self.parser.add_argument("-l", "--logfile",
                                 dest="logfile",
                                 type=str,
                                 help="Path to logfile (optional)")
        self.parser.add_argument("-c", "--logfilecount",
                                 dest="logfilecount",
                                 type=int, default=0,
                                 help="Count of old logfiles to be saved. (default: 0)")
        self.parser.add_argument("-v", "--verbose",
                                 dest="verbose",
                                 action="store_true",
                                 help="vebose output")
        self.parser.add_argument("-s", "--SETTINGS",
                                 dest="settings_module",
                                 type=str,
                                 help="SETTINGS module (required)",
                                 metavar="SETTINGS_MODULE")
        self.parser.add_argument("-r", "--RELOADER",
                                 dest="reloader",
                                 action="store_true",
                                 help="Start with autoreloader")
        self.parser.add_argument("-p", "--pidfile",
                                 dest="pidfile",
                                 type=str,
                                 default="/var/run/%s.pid" % self.name,
                                 help="pidfile")
        
    def parse_args(self):
        args = self.parser.parse_args()
        
        logfile = args.logfile
        logfilecount = args.logfilecount
        self.pidfile = args.pidfile
        self.action = args.action or "foreground"
        self.reloader = args.reloader
        
        if hasattr(args, "settings_module"):
            if args.settings_module:
                os.environ["LEVITAS_SETTINGS"] = args.settings_module
            else:
                self.parser.print_help()
                msg = "option --setting required \n\n"
                raise CLIOptionError(msg)
            
        if self.action == "start":
            self._initLogging(args.verbose, logfile, logfilecount)
        elif self.action == "foreground":
            if logfile is None:
                logfile = "console"
            self._initLogging(args.verbose, logfile, logfilecount)
            
    def _initLogging(self, verbose=False, logfile=None, logfilecount=0):
        log = logging.getLogger()
        if logfile == "console":
            h = logging.StreamHandler()
        elif logfile is not None:
            from logging.handlers import RotatingFileHandler
            doRotation = True if os.path.exists(logfile) else False
            h = RotatingFileHandler(logfile, backupCount=logfilecount)
            if doRotation:
                h.doRollover()
        else:
            return
            
        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            
        formatter = logging.Formatter("%(asctime)s - %(name)s "
                                      "- %(levelname)s - %(message)s")
        h.setFormatter(formatter)
        log.addHandler(h)
            
            