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
import time

from tests import (jsonrpc_test,
                   middleware_test)

    
if __name__ == "__main__":
    #log = logging.getLogger()
    #log.setLevel(logging.DEBUG)
    #handler = logging.StreamHandler()
    #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #handler.setFormatter(formatter)
    #log.addHandler(handler)
    jsonrpc_test.run()
    middleware_test.run()
    