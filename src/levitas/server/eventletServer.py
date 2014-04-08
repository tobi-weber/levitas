# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Tobias Weber <tobi-weber@gmx.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from .baseServer import BaseServer
from levitas.lib import utils


log = logging.getLogger("levitas.server.eventletServer")


class EventletServer(BaseServer):
    """
    Eventlet WSGI Server.
    
    Example SETTINGS entry
    ======================
        # Server address
        httpserver_address = ("127.0.0.1", 8080)
    """
            
    def start(self):
        try:
            import eventlet
            from eventlet import wsgi
            wsgi.server(eventlet.listen(self.server_address,
                                        backlog=500),
                        self.app, max_size=8000)
        except Exception as err:
            log.error(str(err), exc_info=True)
        finally:
            log.info("HTTPD stopped")
