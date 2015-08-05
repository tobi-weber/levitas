# -*- coding: utf-8 -*-
from levitas.lib.settings import Settings
from levitas.middleware import Middleware


class MyMiddleware(Middleware):
    
    def get(self):
        settings = Settings()
        settings.require("custom_attr", example="custom_attr = 'Some string'")
        return settings.custom_attr
