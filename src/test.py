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
from argparse import ArgumentParser

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
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        dest="verbose",
                        action="store_true",
                        help="vebose log output")
    
    # Tests
    parser.add_argument("-m", "--middlewareTest",
                        dest="middlewareTest",
                        action="store_true",
                        help="Middleware-Test")
    parser.add_argument("-j", "--jsonMiddlewareTest",
                        dest="jsonMiddlewareTest",
                        action="store_true",
                        help="JsonMiddleware-Test")
    parser.add_argument("-f", "--fileMiddlewareTest",
                        dest="fileMiddlewareTest",
                        action="store_true",
                        help="FileMiddleware-Test")
    parser.add_argument("-a", "--appMiddlewareTest",
                        dest="appMiddlewareTest",
                        action="store_true",
                        help="AppMiddleware-Test")
    parser.add_argument("-l", "--loggerMiddlewareTest",
                        dest="loggerMiddlewareTest",
                        action="store_true",
                        help="LoggerMiddleware-Test")
    parser.add_argument("-d", "--dynSiteMiddlewareTest",
                        dest="dynSiteMiddlewareTest",
                        action="store_true",
                        help="DynSiteMiddleware-Test")
    
    args = parser.parse_args()
    
    tests = {}
    
    if args.middlewareTest:
        tests["Middleware-Test"] = middlewareTest
    
    if args.jsonMiddlewareTest:
        tests["JsonMiddleware-Test"] = jsonMiddlewareTest
    
    if args.fileMiddlewareTest:
        tests["FileMiddleware-Test"] = fileMiddlewareTest
    
    if args.appMiddlewareTest:
        tests["AppMiddleware-Test"] = appMiddlewareTest
    
    if args.loggerMiddlewareTest:
        tests["LoggerMiddleware-Test"] = loggerMiddlewareTest
    
    if args.dynSiteMiddlewareTest:
        tests["DynSiteMiddleware-Test"] = dynSiteMiddlewareTest
        
    if not tests:
        tests["Middleware-Test"] = middlewareTest
        tests["JsonMiddleware-Test"] = jsonMiddlewareTest
        tests["FileMiddleware-Test"] = fileMiddlewareTest
        tests["AppMiddleware-Test"] = appMiddlewareTest
        tests["LoggerMiddleware-Test"] = loggerMiddlewareTest
        tests["DynSiteMiddleware-Test"] = dynSiteMiddlewareTest
        
    if args.verbose:
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    
    results = {}
    for name, test in tests.items():
        results[name] = test.run()
    
    for k, v in results.items():
        printResult(k, v)
    
if __name__ == "__main__":
    main()
    
    
    