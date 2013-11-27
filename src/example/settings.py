# -*- coding: utf-8 -*-

from levitas.middleware.jsonMiddleware import JSONMiddleware

from .myService import MyService


urls = [
     (r"^/json/myservice", JSONMiddleware, {"service_class": MyService,
                                            "service_attributes":
                                            {"msg": "Hello World!"}
                                            }),
   ]

httpserver_address = ("127.0.0.1", 8080)
