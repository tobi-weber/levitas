# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Tobias Weber <tobi-weber@gmx.de>
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

from levitas.lib.dispatcher import Signal

"""
Signals called by Middleware.

Example:
from levitas.lib.dispatcher import receiver
from levitas.middleware,signals import middleware_request_started

@receiver(middleware_request_started)
def myHandler(**kwargs):
    ...
"""

middleware_instanciated = Signal()
"""
Signal called if a Middleware is instanciated.
"""

middleware_request_started = Signal()
"""
Signal called if a Middleware starts a HTTP Request.
"""

middleware_request_finished = Signal()
"""
Signal called if a Middleware finished a HTTP Request.
"""

