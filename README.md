Levitas
=======

This package provides a lightweight wsgi framework for developing
[JSON-RPC] (http://www.jsonrpc.org) services.

Levitas is designed to be simple to implement and extendable.
It supports version 2 of the [JSON-RPC specification] (http://www.jsonrpc.org).
Also it can serve javascript web applications like written in [pyjamas] (http://pyjs.org/)
or in [rapydscript] (http://rapydscript.pyjeon.com/rapydscript), supports cookie handling,
file uploading and more.


Dependencies
============

* python (>= 2.6)
* [epydoc](http://epydoc.sourceforge.net/) (optional)
* [twisted web](http://twistedmatrix.com) (optional)


Installation
============

Basic installation
-------------------

```
cd src
python setup.py install
```

Build API documentation
-----------------------

```
cd src
epydoc -v --html --debug --no-sourcecode --graph all --output=../api levitas
```

Makefile
--------

Install on local system:

* make install

Generate a deb package:

* make deb

Generate API documentation:

* make doc

Get rid of scratch and byte files:

* make clean


Documentation
=============


Configuration
-------------

Levitas is configured in a settings file. The settings file is 
a Python module with variables. It must be inside PYTHONPATH.
This is inspired by Django settings file.

Here is a complete settings module:
```python
from levitas.middleware.jsonMiddleware import JSONMiddleware
from levitas.middleware.appMiddleware import AppMiddleware
from levitas.middleware.redirectMiddleware import RedirectMiddleware
from levitas.middleware.fileMiddleware import FileMiddleware

"""
A url definition is a tuple of three parts:
 (r"/.*$", MiddlewareClass, {"arg": "value"})
    1. regular expression of the request path.
    2. Middleware class.
    3. Arguments to instantiate the class.
"""
urls = [
	 # JSON-RPC service
     (r"^/json/myservice", JSONMiddleware, {"service_class": MyService}),
     # Site root for static files of your web application
     (r"(?!/json/.*)^/.*$", AppMiddleware, {"path": "/path/to/app"}),
     # Directory with static files
     (r"^/path/to/files/(.*)", FileMiddleware, {"path": "/path/to/files"}),
     # A redirect
     (r"/oldpath", RedirectMiddleware, {"url": "/newpath", "permanent": True})
]

"""
Webserver.
"""
httpserver_address = ("127.0.0.1", 8080)
# httpserver_ssl = True
# httpserver_certfile = "/path/to/certfile"
# httpserver_keyfile = "/path/to/keyfile"


"""
Optional working directory of the wsgi application.
Default is the current working directory.
"""
# working_dir = "/path/to/working directory"

"""
Optional custom path to the favicon.
"""
# favicon = "/path/to/favicon.ico"

"""
Optional encoding settings. Default is utf-8.
"""
# encoding = "utf-8"
           
"""
Optional secret to sign cookies.
"""
# cookie_secret = "my_cookie_secret"
   
"""
Optional path for uploaded files. Default is a tempfile.
"""
# upload_path = "/path/to/upload/files"
```

HTTP JSON-RPC requests and responses
------------------------------------

* The Content-Type can be 'text/json' or 'application/json'
or 'text/json-rpc' or 'application/json-rpc'
* The Content-Length must be specified.
* The POST body contains the Object request specified in [section 4] (http://www.jsonrpc.org/specification).
* Response to a Post contains the Object response specified in [section 5] (http://www.jsonrpc.org/specification).


WSGI
----

To deploy with [WSGI] (http://www.wsgi.org), an object named application
in a Python module is needed:

```python
import os
os.environ["LEVITAS_SETTINGS"] = "my_site.my_settings"

from levitas.handler import WSGIHandler
application = WSGIHandler()
```

WSGI servers:
* [modwsgi for Apache] (http://code.google.com/p/modwsgi/)
* [uwsgi] (http://projects.unbit.it/uwsgi/)


Webserver
=========

Levitas webserver is based on twisted web.

Linux/Unix
----------
 
```
levitas-httpd [OPTION] {start|stop|restart|foreground}

Options:
  -h, --help            show this help message and exit
  -l LOGFILE, --logfile=LOGFILE
                        Path to logfile (optional)
  -c LOGFILECOUNT, --logfilecount=LOGFILECOUNT
                        Count of old logfiles to be saved. (default: 0)
  -v, --verbose         
  -s SETTINGS_MODULE, --settings=SETTINGS_MODULE
                        settings module (required)
  -p PIDFILE, --pidfile=PIDFILE
                        pidfile

```

Example, if the settings module is a python module **my_site/settings.py**:

```
levitas-httpd -s my_site.settings -v foreground
```

Windows
-------

```
Usage: C:\Python27\Scripts\levitas-httpd-service.py [OPTION] {start|stop|remove|install}

Options:
  -h, --help            show this help message and exit
  -n NAME, --name=NAME  Servicename (default: levitasServer)
  -d DISPLAYNAME, --displayname=DISPLAYNAME
                        Displayname (default: Levitas Webserver)
  -a, --stayalive       Service will stop on logout if False (default: True)
  -l LOGFILE, --logfile=LOGFILE
                        Path to logfile (optional)
  -c LOGFILECOUNT, --logfilecount=LOGFILECOUNT
                        Count of old logfiles to be saved. (default: 0)
  -v, --verbose
  -s SETTINGS_MODULE, --settings=SETTINGS_MODULE
                        settings module (required)
```

Install levitas server as a windows service:
```
C:\Python27/Scripts\levitas-httpd-service.py -s my_site.settings -l C:\levitasserver.log -v install
```

Start the service:
```
C:\Python27/Scripts\levitas-httpd-service.py start
```

Example
=======

Here is a small example to show how to write and serve a JSON service.

Write a service **myService.py**:
```python
from levitas.middleware.service import Service


class MyService(Service):
    
    def getMessage(self):
    	# Return the message configured in service_attributes
        return self.msg
    
    def sendMessage(self, msg):
        client = self.middleware.remote_host
        return "Message from %s: %s" % (client, msg)
    
    def _prepare(self):
        """
        Method will be called after service class is instantiated.
        """
        pass
    
    def _complete(self):
        """
        Method will be called after service method is finished.
        """
        pass
```

Write the settings file **settings.py**:
```python
from levitas.middleware.jsonMiddleware import JSONMiddleware

from myService import MyService


urls = [
     (r"^/json/myservice", JSONMiddleware, {"service_class": MyService,
     										"service_attributes":
     										{"msg": "Hello World!"}
     										}),
   ]


httpserver_address = ("127.0.0.1", 8080)
```

Start the server:
```
levitas-httpd -s settings -v foreground
```

Test the service methods in a python console:
```python
>>> import urllib2
>>> headers = {"Content-type": "application/json-rpc"}
>>> opener = urllib2.build_opener()
>>> url = "http://localhost:8080/json/myservice"
>>> data = '{"jsonrpc":"2.0","id":"ID01","method":"getMessage","params": []}'
>>> request = urllib2.Request(url, data=data, headers=headers)
>>> response = opener.open(request)
>>> print response.read()
>>> data = '{"jsonrpc":"2.0","id":"ID02","method":"sendMessage","params": ["Hello Server!"]}'
>>> request = urllib2.Request(url, data=data, headers=headers)
>>> response = opener.open(request)
>>> print response.read()
```



