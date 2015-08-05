# -*- coding: utf-8 -*-
from myMiddleware import MyMiddleware

custom_attr = "Hello World!"

urls = [(r"^/$", MyMiddleware)]
