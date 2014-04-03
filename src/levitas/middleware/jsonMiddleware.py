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

import logging
from json import JSONDecoder, JSONEncoder
from io import BytesIO

from levitas.lib import utils

from .middleware import Middleware
from .service import Service


log = logging.getLogger("levitas.middleware.jsonMiddleware")


CODES = {-32700: "Parse error",
         -32600: "Invalid Request",
         -32601: "Method not found",
         -32602: "Invalid params",
         -32603: "Internal error",
         -32000: "Server error"}


class ServiceImplementationError(Exception):
    pass
        

class JSONMiddleware(Middleware):
    """
    Handles JSON-RPC methods.
    Example:
    from levitas.middleware.service import Service
    
    class MyService(Service):
        
        def my_method(self, arg):
            return arg
            
    
    Example settings entry:
    urls = [(^"/myservice", JSONMiddleware, {"service_class": "MyService",
                                             "service_attributes": {"attr1": VALUE,
                                                                    "attr2": VAUE}
                                            })]
    """
    LOG = True
        
    def __init__(self, service_class, service_attributes={}):
        """
        @param service_class: Class with remote methods.
        @param service_attributes: a dict with attributes for the service.
        """
        Middleware.__init__(self)
        self.service_class = service_class
        self.service_attributes = service_attributes
        if not issubclass(self.service_class, Service):
            raise ServiceImplementationError("""
service class %s must be subclass of levitas.middleware.service.Service
            """ % str(self.service_class))
        
    def post(self):
        try:
            service = self.service_class(self, **self.service_attributes)
            result = ServiceHandler(service).handleData(self.request_data)
            return self.response_result(result)
        except Exception as e:
            utils.logTraceback()
            return self.response_error(500, str(e))
        
    def response_result(self, result):
        f = BytesIO()
        f.write(result.encode(self._encoding))
        self.response_code = 200
        size = f.tell()
        f.seek(0)
        self.addHeader("Content-type", "application/json-rpc; charset=utf-8")
        self.addHeader("Content-Length", str(size))
        self.addHeader("Cache-Control", "no-cache")
        self.start_response()
        return f
        
    
class ServiceHandler:
    def __init__(self, service):
        self.decoder = JSONDecoder(strict=False)
        self.encoder = JSONEncoder(ensure_ascii=True, sort_keys=False)
        self.service = service
        self.retry = False
        
    def handleData(self, data):
        try:
            obj = self.decoder.decode(data)
            result = self.handleRequest(obj)
            return result
        except Exception as err:
            log.error("Internal error: %s" % str(err))
            log.error(data)
            utils.logTraceback()
            return self.__getError(None, -32603, err)

    def handleRequest(self, req):
        """handles a request by calling the appropriete method the service exposes"""
        # id of the request object
        if not "id" in req:
            return self.__getError(None, -32600,
                                   "'id' memeber must be given.")
        idnr = req["id"]
        
        # version of the json-rpc protocol
        if "jsonrpc" in req:
            if not req["jsonrpc"] == "2.0":
                return self.__getError(idnr, -32600,
                                       "json-rpc protocol must be '2.0'.")
        else:
            return self.__getError(idnr, -32600,
                                   "jsonrpc member must be given.")
                
        # method to call
        if not "method" in req:
            return self.__getError(None, -32600,
                                   "'method' memeber must be given.")
        method = req["method"]
        if not hasattr(self.service, method):
            return self.__getError(None, -32601,
                                   "Method %s not found." % method)
        
        # params of the method
        if "params" in req:
            args = req["params"]
            if not isinstance(args, (list, dict)):
                return self.__getError(idnr, -32600,
                                       "params must be either a list or a dictonary")
            if args is None:
                args = []
        else:
            args = []
                        
        obj = None
        try:
            if hasattr(self.service, "_prepare"):
                prepare = getattr(self.service, "_prepare")
                prepare()
            obj = getattr(self.service, method)
            
            if isinstance(args, list):
                data = self.__getResult(idnr, obj(*args))
            elif isinstance(args, dict):
                data = self.__getResult(idnr, obj(**args))
                
            if hasattr(self.service, "_complete"):
                complete = getattr(self.service, "_complete")
                complete()
                
            return data
        except TypeError as err:
            log.error("Invalid params: %s" % str(err))
            utils.logTraceback()
            return self.__getError(idnr, -32602, err)
        except AttributeError as err:
            log.error("Parse error: %s" % str(err))
            utils.logTraceback()
            return self.__getError(idnr, -32700, err)
        except ValueError as err:
            log.error("Parse error: %s" % str(err))
            utils.logTraceback()
            return self.__getError(idnr, -32700, err)
    
    def __getResult(self, idnr, result):
        obj = {"jsonrpc": "2.0", "id": idnr}
        obj["result"] = result
        try:
            return self.encoder.encode(obj)
        except Exception as err:
            log.error("JSON failed to encode: %s" % str(err))
            utils.logTraceback()
            return self.__getError(idnr, -32603, err)
            
    def __getError(self, idnr, code, execption):
        obj = {"jsonrpc": "2.0", "id": idnr}
        error = {"code": code,
                 "message": str(execption),
                 }
        if not isinstance(execption, str):
            error["data"] = {"exception": execption.__class__.__name__,
                             "traceback": utils.getTraceback()}
        else:
            error["data"] = None
            
        obj["error"] = error
        try:
            return self.encoder.encode(obj)
        except Exception as err:
            return self.response_error(500, str(err))
        
        return obj
