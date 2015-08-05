# -*- coding: utf-8 -*-
from myMiddleware import MyMiddleware, MyHandler

urls = [(r"^/.*$", MyMiddleware, MyHandler, "pos-arg-value",
                                 {"named_arg": "named-arg-value"})]
