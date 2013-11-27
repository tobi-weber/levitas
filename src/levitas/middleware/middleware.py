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
import re
import cgi
try:
    from urllib import unquote  # python 2
    from urlparse import urljoin  # python 2
except ImportError:
    from urllib.parse import unquote  # python 3
    from urllib.parse import urljoin  # python 3
import gettext
import calendar
import datetime
import base64
try:
    import Cookie  # python 2
except ImportError:
    import http.cookies as Cookie  # python 3
import time
import email.utils
import hashlib
import hmac
import logging

from levitas.lib.settings import Settings
from levitas.lib import utils

from .signals import (middleware_instanciated,
                     middleware_request_started,
                     middleware_request_finished)
from .errorMiddleware import ErrorMiddleware
from levitas import response_codes


log = logging.getLogger("levitas.middleware.middleware")


class Middleware(object):
    """
    Example settings
    ================
        # Optional encoding settings. Default is utf-8
        encoding = "utf-8"
        
        # A secret to sign cookies
        cookie_secret = "my_cookie_secret"
        
        # Path for uploaded files
        upload_path = "/path/to/upload/files"
    """
    
    SUPPORTED_METHODS = ("get", "head", "post", "delete", "put")
    """ Supported HTTP-Methods """
    
    BLOCKSIZE = 4096
    """ Blocksize for sending files """
    
    LOG = True
    """ If the request should be logged """
    
    def __init__(self, *args, **kwargs):
        
        self.settings = Settings()
        """ Settings-Object """
        
        self.request_headers = {}
        """Headers from the request """
        
        self.response_headers = []
        """ Headers for the response """
        
        self.response_code = 200
        """ Response-code """
        
        self.path = None
        """ path info """
        
        self.arguments = None
        """ Arguments for the GET- or POST-Request """
        
        self.remote_host = None
        """ Remote host of the request """
        
        self.remote_address = None
        """ Remote address of the request """
        
        self.user_agent = None
        """ User agent of the request """
        
        self.cookies = Cookie.BaseCookie()
        """ Cookies for the request """
        
        self._new_cookies = []
        """ New cookies for the response """
        
        if hasattr(self.settings, "encoding"):
            self._encoding = self.settings.encoding
        else:
            self._encoding = "utf-8"
        
        # Send instanciated signal
        middleware_instanciated.send(self.__class__,
                                     middleware=self)
        
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
    
    def addHeader(self, *args):
        """ Add a header to the response """
        self.response_headers.append(args)
        
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
        return self.arguments
    
    def getRemoteHost(self):
        return self.remote_host
    
    def getRemoteAddress(self):
        return self.remote_address
    
    def getUserAgent(self):
        return self.user_agent
        
    def start_response(self, cookies=True):
        """ Start the response """
        s, l = response_codes[self.response_code]  # @UnusedVariable
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
        """ Create an error response """
        error = ErrorMiddleware(code, message)
        return error(self._environ, self._start_response)
    
    def response_redirect(self, url, permanent=False):
        """ Redirect to an url """
        """Sends a redirect to the given (optionally relative) URL."""
        log.debug("redirect to %s" % url)
        self.response_code = 301 if permanent else 302
        # Remove whitespace
        url = url.encode(self._encoding)
        url = re.sub(r"[\x00-\x20]+", "", url)
        self.addHeader("Location", urljoin(self.path,
                                                    url.decode(self._encoding)))
        self.start_response()
        return []
    
    def response_file(self, f):
        """ Send a file """
        if self.filewrapper:
            return self.filewrapper(f, self.BLOCKSIZE)
        else:
            return iter(lambda: f.read(self.BLOCKSIZE), "")
        
    def get_browser_locale(self, default="en"):
        """Determines the user"s locale from Accept-Language header.

        See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
        """
        locales = []
        if "HTTP_ACCEPT_LANGUAGE" in self.request_headers:
            languages = self.request_headers["HTTP_ACCEPT_LANGUAGE"].split(",")
            for language in languages:
                parts = language.strip().split(";")
                if len(parts) > 1 and parts[1].startswith("q="):
                    try:
                        score = float(parts[1][2:])
                    except (ValueError, TypeError):
                        score = 0.0
                else:
                    score = 1.0
                locales.append((parts[0], score))
        return locales
    
    def loadLanguage(self, domain, localedir="/usr/share/locale", default_lang="en"):
        """ Loads a gettext-locale-dir """
        locales = self.get_browser_locale()
        language = default_lang
        for lang, i in locales:  # @UnusedVariable
            if "-" in lang:
                lang = lang.split("-")[0]
            if gettext.find(domain, localedir=localedir, languages=[lang]):
                language = lang
                break
        try:
            language = gettext.translation(domain, localedir=localedir,
                                           languages=[language], fallback=True)
            language.install()
        except:
            pass
        
    def get_cookie(self, name, default=None):
        """ Returns the value of a cookie """
        """Gets the value of the cookie with the given name, else default."""
        if name in self.cookies:
            return self.cookies[name].value.decode(self._encoding)
        return default

    def set_cookie(self, name, value, domain=None, expires=None, path="/",
                   expires_days=None, **kwargs):
        """Sets the given cookie name/value with the given options.

        Additional keyword arguments are set on the Cookie.Morsel
        directly.
        See http://docs.python.org/library/cookie.html#morsel-objects
        for available attributes.
        """
        if re.search(r"[\x00-\x20]", name + value):
            # Don"t let us accidentally inject bad stuff
            raise ValueError("Invalid cookie %r: %r" % (name, value))
        name = name.encode(self._encoding)
        value = value.encode(self._encoding)
        new_cookie = Cookie.BaseCookie()
        new_cookie[name] = value
        if domain:
            new_cookie[name]["domain"] = domain
        if expires_days is not None and not expires:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                days=expires_days)
        if expires:
            timestamp = calendar.timegm(expires.utctimetuple())
            new_cookie[name]["expires"] = email.utils.formatdate(
                timestamp, localtime=False, usegmt=True)
        if path:
            new_cookie[name]["path"] = path
        for k, v in kwargs.items():
            new_cookie[name][k] = v
        
        self._new_cookies.append(new_cookie)

    def clear_cookie(self, name, path="/", domain=None):
        """Deletes the cookie with the given name."""
        #expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        self.set_cookie(name, value="", path=path, expires=expires,
                        domain=domain)

    def clear_all_cookies(self):
        """Deletes all the cookies the user sent with this request."""
        for name in self.cookies.keys():
            self.clear_cookie(name)

    def set_signed_cookie(self, name, value, expires_days=30, **kwargs):
        """Signs and timestamps a cookie so it cannot be forged.

        You must specify the "cookie_secret" setting in your Application
        to use this method. It should be a long, random sequence of bytes
        to be used as the HMAC secret for the signature.

        To read a cookie set with this method, use get_signed_cookie().
        """
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = self._cookie_signature(name, value, timestamp)
        value = "|".join([value, timestamp, signature])
        self.set_cookie(name, value, expires_days=expires_days, **kwargs)

    def get_signed_cookie(self, name):
        """Returns the given signed cookie if it validates, or None.
        """
        value = self.get_cookie(name)
        if not value:
            return None
        
        parts = value.split("|")
        if len(parts) != 3:
            return None
        
        signature = self._cookie_signature(name, parts[0], parts[1])
        if not self._time_independent_equals(parts[2], signature):
            log.warning("Invalid cookie signature %r", value)
            return None
        
        timestamp = int(parts[1])
        if timestamp < time.time() - 31 * 86400:
            log.warning("Expired cookie %r", value)
            return None
        try:
            value = base64.b64decode(parts[0])
        except:
            value = None
            
        return value
    
    def parse_http_datetime(self, s):
        return datetime.datetime(*email.utils.parsedate(s)[:6])
    
    def _cookie_signature(self, *parts):
        """ Create a cookie-signature """
        try:
            secret = self.settings.cookie_secret
        except:
            log.error("Missing cookie_secret in settings!")
            secret = "levitas_cookie_secret"
        h = hmac.new(secret,
                     digestmod=hashlib.sha1)
        for part in parts:
            h.update(part)
        return h.hexdigest()
        
    def _time_independent_equals(self, a, b):
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0
            
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
        
        self._loadCookies()
        
    def _loadCookies(self):
        """ Load the cookies from the response. """
        if "HTTP_COOKIE" in self.request_headers:
            try:
                self.cookies.load(self.request_headers["HTTP_COOKIE"])
            except Exception as err:
                log.error("Error loading cookies: %s" % str(err))
        
    def _parseGET(self):
        """ Parse the query string in the url """
        try:
            arguments = cgi.parse_qs(self.query_string)
            self.arguments = {}
            for name, values in arguments.items():
                values = [v.decode(self._encoding) for v in values if v]
                if values:
                    self.arguments[name.decode(self._encoding)] = values
            return True
        except Exception as err:
            log.error("Failed to parse the form data: %s" % str(err))
            utils.logTraceback()
            return False
        
    def _parsePOST(self):
        """ Parse the form data posted """
        content_length = self.request_headers["CONTENT_LENGTH"]
        content_length = int(content_length)
        content_type = self.request_headers["CONTENT_TYPE"]
        log.debug("POST: %s" % content_type)
        try:
            if content_type.startswith("text/json") or \
                content_type.startswith("application/json"):
                    self.arguments = self.input.read(content_length)
                    self.arguments = self.arguments.decode(self._encoding)
                    self.arguments = unquote(self.arguments)
                
            elif content_type.startswith("application/x-www-form-urlencoded"):
                request_body = self.input.read(content_length)
                self.arguments = cgi.parse_qs(request_body)
                
            elif content_type.startswith("multipart/form-data"):
                log.debug("Multipart/form-data request")
                log.debug("Content-Length: %d" % content_length)
                if not content_length:
                    return False
                if hasattr(self.settings, "upload_path"):
                    log.debug("Upload-Path: %s" % self.settings.upload_path)
                    MyFieldStorage.temppath = self.settings.upload_path
                self.arguments = MyFieldStorage(fp=self.input,
                                                  environ=self._environ,
                                                  keep_blank_values=True,
                                                  strict_parsing=False)
            return True
        except Exception as err:
            log.error("Failed to parse the form data: %s" % str(err))
            utils.logTraceback()
            return False
    
    def __call__(self, environ, start_response):
        self._start_response = start_response
        self._environ = environ
        self._readEnviron(environ)
        
        if self.request_method not in self.SUPPORTED_METHODS:
            log.error("Unknown method %s" % self.request_method)
            return self.response_error(405, "method %s unsupported"
                                       % self.request_method)
        
        try:
            
            # Parse arguments for a GET or POST request
            if self.request_method == "get":
                if self.query_string:
                    if not self._parseGET():
                        return self.response_error(500)
            elif self.request_method == "post":
                if not self._parsePOST():
                    return self.response_error(500)
                
            # Send request started signal
            middleware_request_started.send(self.__class__,
                                            middleware=self)
            
            # call prepare
            self.prepare()
            
            # call the request-method
            result = getattr(self, self.request_method)()
            
            if isinstance(result, str):
                result = result.encode(self._encoding)
                
            if isinstance(result, bytes):
                return [result]
            else:
                return result
        
        except:
            utils.logTraceback()
            return self.response_error(500)
        

class MyFieldStorage(cgi.FieldStorage):
    
    temppath = None
     
    def make_file(self, binary=None):
        log.debug("Handling Fileupload")
        if self.temppath:
            if not os.path.exists(self.temppath):
                log.debug("Create temppath %s" % self.temppath)
                os.mkdir(self.temppath)
            # strip leading path from f name to avoid directory traversal attacks
            filename = os.path.basename(self.filename)
            filepath = os.path.join(self.temppath, filename)
            log.debug("Create filepath %s" % filepath)
            f = open(filepath, "wb")
            return f
        else:
            import tempfile
            log.debug("Create Tempfile")
            return tempfile.TemporaryFile(mode="w+b")
