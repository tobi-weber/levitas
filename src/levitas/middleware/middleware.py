# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Tobias Weber <tobi-weber@gmx.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this FILE except in compliance with the License.
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
import sys
import re
import cgi
import time
try:
    from urllib import quote, unquote  # python 2
    from urlparse import urljoin, parse_qs  # python 2
except ImportError:
    from urllib.parse import quote, unquote  # python 3
    from urllib.parse import urljoin, parse_qs  # python 3
try:
    import Cookie  # python 2
except ImportError:
    import http.cookies as Cookie  # python 3
import logging
from io import BytesIO
if sys.version_info[0] == 3:
    import _io
    FILE = _io.BufferedReader
    STR = str
else:
    STR = unicode
    FILE = file
from levitas.lib.settings import Settings
from levitas.lib import utils
from levitas.lib.secure_cookie import SecureCookie
from .signals import (middleware_instanciated,
                     middleware_request_started,
                     middleware_request_finished)
from levitas import (DEFAULT_ERROR_MESSAGE_FORMAT,
                     DEFAULT_ERROR_CONTENT_TYPE,
                     response_codes)


log = logging.getLogger("levitas.middleware.middleware")


class Middleware(object):
    """
    Example settings
    ================
        # Optional encoding settings. Default is utf-8
        encoding = "utf-8"
        
        # A secret to sign cookies
        cookie_secret = "my_cookie_secret"
        
        # Custom cgi.FieldStorage class
        fieldstorage_class = LevitasFieldStorage
    """
    
    SUPPORTED_METHODS = ("get", "head", "post", "delete", "put")
    """ Supported HTTP-Methods """
    
    BLOCKSIZE = 4096
    """ Blocksize for sending files """
    
    LOG = True
    """ If the request should be logged """
    
    ERROR_MESSAGE_FORMAT = DEFAULT_ERROR_MESSAGE_FORMAT
    ERROR_CONTENT_TYPE = DEFAULT_ERROR_CONTENT_TYPE
    
    def __init__(self, *args, **kwargs):
        
        self.settings = Settings()
        """ Settings-Object """
        
        self.request_method = None
        """ HTTP-Request method """
        
        self.request_headers = {}
        """Headers from the request """
        
        self.response_headers = []
        """ Headers for the response """
        
        self.response_code = 200
        """ Response-code """
        
        self.path = None
        """ path info """
        
        self.request_data = None
        """ Request data """
        
        self.remote_host = None
        """ Remote host of the request """
        
        self.remote_address = None
        """ Remote address of the request """
        
        self.user_agent = None
        """ User agent of the request """
        
        self.url_scheme = None
        """ Url scheme (http or https) """
        
        self.server_name = None
        """ Server name """
        
        self.server_port = None
        """ Server port """
        
        self.query_string = None
        """ Query string """
        
        self.cookies = Cookie.BaseCookie()
        """ Cookies for the request """
        
        self._new_cookies = []
        """ New cookies for the response """
        
        self.__responseStarted = False
        
        if hasattr(self.settings, "encoding"):
            self._encoding = self.settings.encoding
        else:
            self._encoding = "utf-8"
        
        if hasattr(self.settings, "fieldstorage_class"):
            self._fieldstorage_class = self.settings.fieldstorage_class
        else:
            self._fieldstorage_class = cgi.FieldStorage
        
        # Send instanciated signal
        middleware_instanciated.send(self.__class__,
                                     middleware=self)
        
    def initEnviron(self, environ, start_response):
        """ Initialize the wsgi environment """
        self._start_response = start_response
        self._environ = environ
        self._readEnviron(environ)
        self._loadCookies()
        
    def log_request(self, code="-", size="-"):
        if self.LOG:
            self.log_message(logging.INFO, '"%s %s" %s %s',
                              self.request_method, self.path, str(code), str(size))

    def log_error(self, f, *args):
        self.log_message(logging.ERROR, f, *args)

    def log_message(self, level, f, *args):
        msg = "(%s) " % os.getpid() + f % args + " " + self.remote_host
        log.log(level, msg)
        
    def prepare(self):
        """ Called before the request-method is called. """
        pass

    def head(self):
        """ Can be overwritten by subclass """
        log.error("head method not implemented in %s" % str(self.__class__))
        return self.response_error(405)

    def get(self):
        """ Can be overwritten by subclass """
        log.error("get method not implemented in %s" % str(self.__class__))
        return self.response_error(405)

    def post(self):
        """ Can be overwritten by subclass """
        log.error("post method not implemented in %s" % str(self.__class__))
        return self.response_error(405)

    def delete(self):
        """ Can be overwritten by subclass """
        log.error("delete method not implemented in %s" % str(self.__class__))
        return self.response_error(405)
    
    def put(self):
        """ Maybe overwritten by subclass """
        log.error("put method not implemented in %s" % str(self.__class__))
        return self.response_error(405)
    
    def getPath(self):
        return self.path
    
    def addHeader(self, name, value):
        """ Add a header to the response """
        self.response_headers.append((str(name), str(value)))
        
    def getHeader(self, name):
        name = name.upper()
        if name in self.request_headers:
            return self.request_headers[name]
        else:
            return None
        
    def getResponseCode(self):
        return self.response_code
    
    def setResponseCode(self, response_code=200):
        self.response_code = response_code
        
    def getArguments(self):
        return self.request_data
    
    def getRemoteHost(self):
        return self.remote_host
    
    def getRemoteAddress(self):
        return self.remote_address
    
    def getUserAgent(self):
        return self.user_agent
        
    def start_response(self, cookies=True):
        """ Start the response """
        log.debug("Start response")
        if self.__responseStarted:
            log.error("Response already started")
            return
        self.__responseStarted = True
        try:
            s, l = response_codes[self.response_code]  # @UnusedVariable
        except KeyError:
            s, l = "???", "???"  # @UnusedVariable
        status = "%s %s" % (str(self.response_code), s)
        
        if self.response_code == 200 and cookies:
            for cookie in self._new_cookies:
                for name in cookie:
                    self.addHeader("Set-Cookie", cookie[name].OutputString())
                
        #self.addHeader("Accept-Ranges", "bytes")
        
        self.log_request(self.response_code)
        
        self.output = self._start_response(status, self.response_headers)
        
        # Send request finished signal
        middleware_request_finished.send(self.__class__,
                                         middleware=self)
        
    def response_error(self, code, message=None):
        self.__responseStarted = True
        log.debug("response_error: %s - %s" % (str(code), str(message)))
        try:
            short, l = response_codes[code]
        except KeyError:
            short, l = "???", "???"
        if message is None:
            message = short
        explain = l
        log.error("code %d, message: %s", code, message)
        content = (Middleware.ERROR_MESSAGE_FORMAT %
                   {"code": code,
                    "message": quote(message),
                    "explain": explain})
        f = BytesIO()
        f.write(content.encode(self._encoding))
        size = f.tell()
        f.seek(0)
        headers = [("Content-Type", Middleware.ERROR_CONTENT_TYPE)]
        status = "%s %s" % (str(code), short)
        if self.request_method != "head" and code >= 200 and code not in (204, 304):
            headers.append(("Content-Length", str(size)))
            self._start_response(status, headers, sys.exc_info())
            return f
        else:
            headers.append(("Content-Length", "0"))
            self._start_response(status, headers)
            return
    
    def response_redirect(self, url, permanent=False):
        """ Redirect to an url """
        """Sends a redirect to the given (optionally relative) URL."""
        log.debug("redirect to %s" % url)
        self.response_code = 301 if permanent else 302
        # Remove whitespace
        url = re.sub(r"[\x00-\x20]+", "", url)
        url = url.encode(self._encoding)
        self.addHeader("Location", urljoin(self.path,
                                           url.decode(self._encoding)))
        return
    
    def response_file(self, f):
        """ Send a FILE """
        if self.filewrapper:
            return self.filewrapper(f, self.BLOCKSIZE)
        else:
            return iter(lambda: f.read(self.BLOCKSIZE), "")
        
    def get_browser_language(self):
        """Determines the user's locale from Accept-Language header.

        See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
        """
        locales = []
        if "HTTP_ACCEPT_LANGUAGE" in self.request_headers:
            languages = self.request_headers["HTTP_ACCEPT_LANGUAGE"].split(",")
            for language in languages:
                parts = language.strip().split(";")
                locales.append(parts[0])
        return locales
        
    def get_cookie(self, name, default=None):
        """ Returns the value of a cookie """
        """Gets the value of the cookie with the given name, else default."""
        if name in self.cookies:
            return self.cookies[name].value
        return default

    def set_cookie(self, name, value,
                   domain=None, path="/", httponly=False,
                   expires=None,
                   expires_days=None,
                   expires_hours=None,
                   expires_minutes=None,
                   **kwargs):
        """Sets the given cookie name/value with the given options.

        Additional keyword request_data are set on the Cookie.Morsel
        directly.
        See http://docs.python.org/library/cookie.html#morsel-objects
        for available attributes.
        """
        
        # Cookie accepts only type str in both Python 2 and 3 
        if sys.version_info[0] == 3:
            if isinstance(name, bytes):
                name = name.decode(self._encoding)
            if isinstance(value, bytes):
                value = value.decode(self._encoding)
        else:
            if isinstance(name, unicode):
                name = name.encode(self._encoding)
            if isinstance(value, unicode):
                value = value.encode(self._encoding)
        
        if re.search(r"[\x00-\x20]", name + value):
            # Don"t let us accidentally inject bad stuff
            raise ValueError("Invalid cookie %r: %r" % (name, value))
        
        new_cookie = Cookie.BaseCookie()
        new_cookie[name] = value
        if domain:
            new_cookie[name]["domain"] = domain
        
        # Set expires
        if expires is not None:
            new_cookie[name]["expires"] = expires
        elif expires_days or expires_hours or expires_minutes:
            t = time.time()
            if expires_days:
                t += expires_days * 24 * 60 * 60
            if expires_hours:
                t += expires_hours * 60 * 60
            if expires_minutes:
                t += expires_minutes * 60
                # Tue 08-Apr-2014 14:04:24 GMT
            new_cookie[name]["expires"] = utils.time2netscape(t)
        if path:
            new_cookie[name]["path"] = path
            
        if httponly:
            new_cookie[name]["httponly"] = True
            
        for k, v in kwargs.items():
            new_cookie[name][k] = v
        
        self._new_cookies.append(new_cookie)

    def clear_cookie(self, name, path="/", domain=None):
        """Deletes the cookie with the given name."""
        #expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        if name in self.cookies:
            t = time.time() - (365 * 24 * 60 * 60)
            expires = utils.time2netscape(t)
            self.set_cookie(name, "", path=path, expires=expires,
                            domain=domain)
        else:
            log.error("Cookie %s does not exist" % name)

    def clear_all_cookies(self):
        """Deletes all the cookies the user sent with this request."""
        for name in self.cookies.keys():
            self.clear_cookie(name)

    def set_signed_cookie(self, name, value,
                   domain=None, path="/", httponly=False,
                   expires=None,
                   expires_days=None,
                   expires_hours=None,
                   expires_minutes=None,
                   **kwargs):
        """Signs and timestamps a cookie so it cannot be forged.

        You must specify the "cookie_secret" setting in your settings FILE
        to use this method. It should be a long, random sequence of bytes
        to be used as the HMAC secret for the signature.

        To read a cookie set with this method, use get_signed_cookie().
        """
        value = SecureCookie().encode_value(name, value)
        self.set_cookie(name, value,
                        domain=domain,
                        path=path,
                        httponly=httponly,
                        expires_days=expires_days,
                        expires_hours=expires_hours,
                        expires_minutes=expires_minutes,
                        **kwargs)

    def get_signed_cookie(self, name):
        """Returns the given signed cookie if it validates, or None.
        """
        value = self.get_cookie(name)
        
        return SecureCookie().decode_value(name, value)
            
    def _readEnviron(self, environ):
                
        for k, v in environ.items():
            if "HTTP_" in k or \
                "CONTENT_" in k:
                self.request_headers[k] = v
        
        self.path = environ["PATH_INFO"]
        self.input = environ["wsgi.input"]
        if "wsgi.file_wrapper" in environ:
            self.filewrapper = environ["wsgi.file_wrapper"]
        else:
            self.filewrapper = None
        self.output = None
                
        self.url_scheme = environ["wsgi.url_scheme"]
        self.server_name = environ["SERVER_NAME"]
        self.server_port = environ["SERVER_PORT"]
        
        self.remote_host = ""
        if "REMOTE_HOST" in environ:
            self.remote_host = environ["REMOTE_HOST"]
        
        self.http_host = ""
        if "HTTP_HOST" in environ:
            http_host = environ["HTTP_HOST"]
            if ":" in http_host:
                http_host = http_host.split(":")[0]
            self.http_host = http_host
        
        if not self.remote_host:
            self.remote_host = self.http_host
            
        if "HTTP_ADDR" in environ:
            self.remote_address = environ["HTTP_ADDR"]
        elif "REMOTE_ADDR" in environ:
            self.remote_address = environ["REMOTE_ADDR"]
        else:
            self.remote_address = ""
            
        if self.remote_host == "localhost" \
            and "::" in self.remote_address:
            self.remote_address = "127.0.0.1"
        
        if "HTTP_USER_AGENT" in environ:
            self.user_agent = self.request_headers["HTTP_USER_AGENT"]
        else:
            self.user_agent = "UNKNOWN USER-AGENT"
        self.request_method = environ["REQUEST_METHOD"].lower()
        self.query_string = environ.get("QUERY_STRING")
        
    def _loadCookies(self):
        """ Load the cookies from the response. """
        if "HTTP_COOKIE" in self.request_headers:
            try:
                self.cookies.load(self.request_headers["HTTP_COOKIE"])
            except Exception as err:
                raise
                log.error("Error loading cookies: %s" % str(err))
                
    def _parse_qs(self, qs):
        try:
            arguments = parse_qs(qs)
            self.request_data = {}
            for name, _values in arguments.items():
                values = []
                for v in _values:
                    if v:
                        if not isinstance(v, STR):
                            v = v.decode(self._encoding)
                        values.append(v)
                if values:
                    if not isinstance(name, STR):
                        name = name.decode(self._encoding)
                    self.request_data[name] = values
            return True
        except Exception as err:
            log.error("Failed to parse the form data: %s" % str(err))
            utils.logTraceback()
            return False
        
    def _parseGET(self):
        """ Parse the query string in the url """
        return self._parse_qs(self.query_string)
        
    def _parsePOST(self):
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
                
            elif content_type.startswith("application/x-www-form-urlencoded"):
                request_body = self.input.read(content_length)
                return self._parse_qs(request_body)
                
            elif content_type.startswith("multipart/form-data"):
                log.debug("Multipart/form-data request")
                if not content_length:
                    return False
                self.request_data = self._fieldstorage_class(fp=self.input,
                                                  environ=self._environ,
                                                  keep_blank_values=True,
                                                  strict_parsing=False)
            return True
        except Exception as err:
            log.error("Failed to parse the form data: %s" % str(err))
            utils.logTraceback()
            return False
    
    def __call__(self, environ, start_response):
        self.initEnviron(environ, start_response)
        log.info(self.path)
        
        if self.request_method not in self.SUPPORTED_METHODS:
            log.error("Unknown method %s" % self.request_method)
            return self.response_error(405, "method %s unsupported"
                                       % self.request_method)
        
        try:
            
            # Parse request_data for a GET or POST request
            if self.request_method == "get":
                if self.query_string:
                    if not self._parseGET():
                        return self.response_error(500, "Error parsing query string")
            elif self.request_method == "post":
                if not self._parsePOST():
                    return self.response_error(500, "Error parsing post data")
                
            # Send request started signal
            middleware_request_started.send(self.__class__,
                                            middleware=self)
            
            # call prepare
            self.prepare()
            
            # call the request-method
            result = getattr(self, self.request_method)()
            
            # Do not return empty/invalid results
            if isinstance(result, list):
                if not len(result):
                    result = b""
            elif result is None:
                result = b""
            elif not hasattr(result, "__iter__") and \
                not isinstance(result, (STR, bytes, FILE)):
                return self.response_error(500,
                                           "%s: Method %s returns not iterable object %s"
                                           % (self.__class__.__name__,
                                              self.request_method,
                                              type(result)))
                
            if not self.__responseStarted:
                self.start_response()
                
            log.debug("Response type: %s" % type(result))
            # Encode unicode(python2.7)/str(python3) type to bytes type
            if isinstance(result, STR):
                result = result.encode(self._encoding)
            
            # Return the result
            if isinstance(result, bytes):
                result = [result]
                
            if isinstance(result, FILE):
                log.debug("Send FILE")
                return self.response_file(result)
            else:
                log.debug("Send data")
                return result
        
        except:
            utils.logTraceback()
            return self.response_error(500)
        
