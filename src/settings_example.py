# -*- coding: utf-8 -*-

#from levitas.middleware.jsonMiddleware import JSONMiddleware
#from levitas.middleware.appMiddleware import AppMiddleware
#from levitas.middleware.redirectMiddleware import RedirectMiddleware
#from levitas.middleware.fileMiddleware import FileMiddleware


"""
A url definition is a tuple with three parts:
 (r"/.*$", MiddlewareClass, {"arg": "value"})
    1. regular expression of the request path.
    2. Middleware class.
    3. Arguments to instantiate the class.
    
Tuple examples:
    - Define a JSON-RPC service:
        (r"^/json/myservice", JSONMiddleware, {"service_class": MyService})
    - Define a site root for the static files of your web application:
        (r"(?!/json/.*)^/.*$", AppMiddleware, {"path": "/path/to/app"})
    - Define another directory with static files:
        r"^/path/to/files/(.*)", FileMiddleware, {"path": "/path/to/files"})
    - Define a redirect:
        (r"/oldpath", RedirectMiddleware, {"url": "/newpath", "permanent": True})
"""
#urls = [
#     (r"^/json/myservice", JSONMiddleware, {"service_class": MyService}),
#     (r"(?!/json/.*)^/.*$", AppMiddleware, {"path": "/path/to/app"}),
#     (r"^/path/to/files/(.*)", FileMiddleware, {"path": "/path/to/files"}),
#     (r"/oldpath", RedirectMiddleware, {"url": "/newpath", "permanent": True})
#]


"""
Integrated webserver.
"""
# httpserver_address = ("127.0.0.1", 8080)
# httpserver_ssl = False
# httpserver_certfile = "/path/to/certfile"
# httpserver_keyfile = "/path/to/keyfile"


"""
Working directory of the wsgi application.
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
Optional path for uploaded files. Default is a temp file.
"""
# upload_path = "/path/to/upload/files"

