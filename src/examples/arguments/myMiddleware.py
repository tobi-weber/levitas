# -*- coding: utf-8 -*-
from levitas.middleware import Middleware


class MyHandler(object):

    def __init__(self, pos_arg, named_arg="value"):
        self.pos_arg = pos_arg
        self.named_arg = named_arg

    def get_result(self):
        return "Handler called with pos_arg '%s' and named_arg '%s'" \
                % (self.pos_arg, self.named_arg)


class MyMiddleware(Middleware):

    def __init__(self, handler_class, pos_arg, named_arg="value"):
        Middleware.__init__(self)
        self.handler_class = handler_class
        self.pos_arg = pos_arg
        self.named_arg = named_arg

    def get(self):
        handler = self.handler_class(self.pos_arg,
                                     named_arg=self.named_arg)
        return handler.get_result()
