# -*- coding: utf-8 -*-
from levitas.middleware import Middleware


class MyMiddleware(Middleware):
    def get(self):
        return "Hello world!"
