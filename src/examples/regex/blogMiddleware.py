# -*- coding: utf-8 -*-
from levitas.middleware import Middleware


class BlogMiddleware(Middleware):
    def get(self):
        year, month, date = self.url_groups()
        return "Blog entry %s-%s-%s" % (year, month, date)
