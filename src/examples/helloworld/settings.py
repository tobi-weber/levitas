# -*- coding: utf-8 -*-
from myMiddleware import MyMiddleware

urls = [(r"^/$", MyMiddleware)]
