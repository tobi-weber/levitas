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

import logging
from json import JSONDecoder, JSONEncoder
from io import BytesIO
try:
    from urllib import unquote  # python 2
except ImportError:
    from urllib.parse import unquote  # python 3

from levitas.lib import utils

from . import Middleware


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
    urls = [(r"^/myservice$", JSONMiddleware, MyService,
                                            {"service_attributes": {"attr1": VALUE,
                                                                    "attr2": VAUE}
                                            })]
    """
    LOG = True
        
    def __init__(self, service_class, *service_args, **service_kwargs):
        """
        @param service_class: Class with remote methods.
        """
        Middleware.__init__(self)
        self.service_class = service_class
        self.service_args = service_args
        self.service_kwargs = service_kwargs
        
    def post(self):
        try:
            service = self.service_class(*self.service_args, **self.service_kwargs)
            setattr(service, "middleware", self)
            result = ServiceHandler(service).handleData(self.request_data)
            return self.response_result(result)
        except Exception as e:
            log.debug(str(e), exc_info=True)
            return self.responseError(500, str(e))
        
    def response_result(self, result):
        f = BytesIO()
        f.write(result.encode(self._encoding))
        self.response_code = 200
        size = f.tell()
        f.seek(0)
        self.addHeader("Content-type", "application/json-rpc; charset=utf-8")
        self.addHeader("Content-Length", str(size))
        self.addHeader("Cache-Control", "no-cache")
        self._startResponse()
        return f
        
    def parsePOST(self):
        """ Parse the form data posted """
        content_length = self.request_headers["CONTENT_LENGTH"]
        content_length = int(content_length)
        content_type = self.request_headers["CONTENT_TYPE"]
        log.debug("POST: %s, Content-Length: %d" % (content_type, content_length))
        try:
            if content_type.startswith("text/json") or \
                content_type.startswith("application/json"):
                self.request_data = self.input.read(content_length)
                self.request_data = self.request_data.decode(self._encoding)
                self.request_data = unquote(self.request_data)
                log.debug("POST data parsed")
                return 0
            else:
                log.error("Wrong content type")
                return 415
        except Exception as err:
            log.error("Failed to parse the form data: %s" % str(err), exc_info=True)
            return 500
        
    
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
            log.error(data, exc_info=True)
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
            log.error("Invalid params: %s" % str(err), exc_info=True)
            return self.__getError(idnr, -32602, err)
        except AttributeError as err:
            log.error("Parse error: %s" % str(err), exc_info=True)
            return self.__getError(idnr, -32700, err)
        except ValueError as err:
            log.error("Parse error: %s" % str(err), exc_info=True)
            return self.__getError(idnr, -32700, err)
    
    def __getResult(self, idnr, result):
        obj = {"jsonrpc": "2.0", "id": idnr}
        obj["result"] = result
        try:
            return self.encoder.encode(obj)
        except Exception as err:
            log.error("JSON failed to encode: %s" % str(err), exc_info=True)
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
            return self.responseError(500, str(err))
        
        return obj
