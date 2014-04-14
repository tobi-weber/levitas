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

from tests import (jsonMiddlewareTest,
                   middlewareTest,
                   fileMiddlewareTest,
                   loggerMiddlewareTest,
                   appMiddlewareTest,
                   dynSiteMiddlewareTest)

SEPERATOR1 = "=" * 70
SEPERATOR2 = "-" * 70


def printResult(name, res):
    def printError(flavour, errors):
        for test, err in errors:
            print("")
            print("%s: %s" % (flavour, res.getDescription(test)))
            print(SEPERATOR2)
            print("%s" % err)
    print("")
    print(SEPERATOR1)
    print("%s %d tests" % (name, res.testsRun))
    print(SEPERATOR2)
    print("Errors: %d" % len(res.errors))
    print("Failures: %d" % len(res.failures))
    if res.errors:
        printError("ERROR", res.errors)
    if res.failures:
        printError("FAIL", res.failures)
    print("")
    
    
def main():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    results = {}
    results["Middleware"] = middlewareTest.run()
    results["JsonMiddleware"] = jsonMiddlewareTest.run()
    results["FileMiddleware"] = fileMiddlewareTest.run()
    results["LoggerMiddleware"] = loggerMiddlewareTest.run()
    results["AppMiddleware"] = appMiddlewareTest.run()
    results["DynSiteMiddlewareTest"] = dynSiteMiddlewareTest.run()
    
    for k, v in results.items():
        printResult(k, v)
    
if __name__ == "__main__":
    main()
    
    
    