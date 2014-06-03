# -*- coding: utf-8 -*-
# Copyright (C) 2013 Tobias Weber <tobi-weber@gmx.de>

import sys
import os
import logging
from argparse import ArgumentParser

import win32api  # @UnresolvedImport
import win32serviceutil  # @UnresolvedImport
import win32service  # @UnresolvedImport
#import win32event  # @UnresolvedImport


def cli(cls, name, displayname=None, stay_alive=True):
    ''' Install and  Start (auto) a Service
            
        cls : the class (derived from Service) that implement the Service
        name : Service name
        displayname : the name displayed in the service manager
        stay_alive : Service will stop on logout if False
    '''
    def log(msg):
        import servicemanager  # @UnresolvedImport
        servicemanager.LogInfoMsg(str(msg))
        
    options = CLIOptions(name, displayname, stay_alive)
    try:
        options.parse_args()
    except CLIOptionError:
        sys.exit(1)
    
    print("%s %s " % (options.action or "start", name))

    cls._svc_name_ = options.name
    cls._svc_display_name_ = options.displayname or options.name
    
    if options.action == "install":
        try:
            module_path = sys.modules[cls.__module__].__file__
        except AttributeError:
            # maybe py2exe went by
            from sys import executable
            module_path = executable
        
        module_file = os.path.splitext(os.path.abspath(module_path))[0]
        cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
        if options.stay_alive:
            win32api.SetConsoleCtrlHandler(lambda x: True, True)
        try:
            win32serviceutil.InstallService(
                cls._svc_reg_class_,
                cls._svc_name_,
                cls._svc_display_name_,
                startType = win32service.SERVICE_AUTO_START
            )
            
            # Set options to registry
            print("Add settings_module to registry: %s" % options.settings_module)
            win32serviceutil.SetServiceCustomOption(cls._svc_name_,
                                                    "settings_module",
                                                    options.settings_module)
            print("Add logfile to registry: %s" % str(options.logfile))
            win32serviceutil.SetServiceCustomOption(cls._svc_name_,
                                                    "logfile",
                                                    str(options.logfile))
            print("Add logfilecount to registry: %s" % str(options.logfilecount))
            win32serviceutil.SetServiceCustomOption(cls._svc_name_,
                                                    "logfilecount",
                                                    str(options.logfilecount))
            print("Add verbose to registry: %s" % str(options.verbose))
            win32serviceutil.SetServiceCustomOption(cls._svc_name_,
                                                    "verbose",
                                                    str(options.verbose))
            print('Install ok')
        except Exception as x:
            print(str(x))
            
    elif options.action == "start":
        try:
            win32serviceutil.StartService(
                cls._svc_name_
            )
            print('Start ok')
        except Exception as x:
            print(str(x))
            
    elif options.action == "stop":
        try:
            win32serviceutil.StopService(
                cls._svc_name_
            )
            print('Stop ok')
        except Exception as x:
            print(str(x))
            
    elif options.action == "restart":
        try:
            win32serviceutil.RestartService(
                cls._svc_name_
            )
            print('Restart ok')
        except Exception as x:
            print(str(x))
            
    elif options.action == "remove":
        try:
            win32serviceutil.RemoveService(
                cls._svc_name_
            )
            print('Remove ok')
        except Exception as x:
            print(str(x))


class WinService(win32serviceutil.ServiceFramework):
    
    _svc_name_ = "pyService"
    _svc_display_name_ = ""
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        
        self.log(self.__class__._svc_name_)
        self.log(self.__class__._svc_display_name_)
        # Get options from registry
        self._settings_module = \
        win32serviceutil.GetServiceCustomOption(self.__class__._svc_name_,
                                                "settings_module")
        self.log("load settings_module: %s" % str(self._settings_module))
        self._logfile = \
        win32serviceutil.GetServiceCustomOption(self.__class__._svc_name_,
                                                "logfile")
        self.log("load logfile: %s" % str(self._logfile))
        if self._logfile == "None":
            self._logfile = None
            
        self._logfilecount = \
        win32serviceutil.GetServiceCustomOption(self.__class__._svc_name_,
                                                "logfilecount")
        self.log("load logfilecount: %s" % str(self._logfilecount))
        try:
            self._logfilecount = int(self._logfilecount)
        except:
            self._logfilecount = 0
        
        self._verbose = \
        win32serviceutil.GetServiceCustomOption(self.__class__._svc_name_,
                                                "verbose")
        self.log("load verbose: %s" % str(self._verbose))
        self._verbose = self._verbose == "True"
        
        os.environ["LEVITAS_SETTINGS"] = self._settings_module
        self._initLogging()

    def SvcStop(self):
        self.log("Stop server")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()

    def SvcDoRun(self):
        self.log("SvcDoRun")
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        
        # start server
        self.log("Start server")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        self.start()
        
        self.log("server stopped")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        
    def log(self, msg):
        import servicemanager  # @UnresolvedImport
        servicemanager.LogInfoMsg(str(msg))
        
    def _initLogging(self):
        if self._logfile is None:
            return
        
        from logging.handlers import TimedRotatingFileHandler
        log = logging.getLogger()
        formatter = logging.Formatter("%(asctime)s - %(name)s "
                                  "- %(levelname)s - %(message)s")
        h = TimedRotatingFileHandler(self._logfile, when="midnight",
                                     backupCount=self._logfilecount)
        h.doRollover()
        
        if self._verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            
        h.setFormatter(formatter)
        log.addHandler(h)
    
    def start(self):
        pass
            
    def stop(self):
        pass
        
        
class CLIOptionError(Exception):
    pass


class CLIOptions(object):
    
    def __init__(self, name, displayname, stay_alive):
        self.name = name
        self.displayname = displayname
        self.stay_alive = stay_alive
        
        self.parser = ArgumentParser()
        
        self.parser.add_argument("action", type=str,
                                 choices=["start", "stop", "remove", "install"])
        self.parser.add_argument("-n", "--name",
                       dest="name",
                       help="Servicename (default: %s)" % self.name,
                       default=self.name)
        self.parser.add_argument("-d", "--displayname",
                       dest="displayname",
                       help="Displayname (default: %s)" % self.displayname,
                       default=self.displayname)
        self.parser.add_argument("-a", "--stayalive",
                       dest="stay_alive",
                       help="Service will stop on logout if False (default: %s)"\
                            % str(self.stay_alive),
                       default=self.stay_alive,
                       action="store_true")
        self.parser.add_argument("-l", "--logfile",
                       dest="logfile",
                       help="Path to logfile (optional)")
        self.parser.add_argument("-c", "--logfilecount",
                       dest="logfilecount",
                       type="int", default=0,
                       help="Count of old logfiles to be saved. (default: 0)")
        self.parser.add_argument("-v", "--verbose",
                       dest="verbose",
                       action="store_true")
        self.parser.add_argument("-s", "--settings",
                       dest="settings_module",
                       help="settings module (required)",
                       metavar="SETTINGS_MODULE")
        
    def parse_args(self):
        args = self.parser.parse_args()
            
        self.action = args.action
        self.name = args.name
        self.displayname = args.displayname
        self.stay_alive = args.stay_alive
        self.logfile = args.logfile
        self.logfilecount = args.logfilecount
        self.verbose = args.verbose
        
        if hasattr(args, "settings_module"):
            if args.settings_module:
                self.settings_module = args.settings_module
            else:
                if self.action == "install":
                    self.parser.print_help()
                    raise CLIOptionError("option --settings required")

            
            