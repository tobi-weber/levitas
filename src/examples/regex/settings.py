# -*- coding: utf-8 -*-
from blogMiddleware import BlogMiddleware

urls = [(r"^/blog/(\d{4})/(\d{2})/(\d{2})$", BlogMiddleware)]
