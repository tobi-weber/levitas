# -*- coding: utf-8 -*-
#   Copyright (C) 2010-2013 Tobias Weber <tobi-weber@gmx.de>

import platform
from distutils.core import setup


if platform.system() == "Windows":
    scripts = ["levitas-testserver-service.py"]
else:
    scripts = ["levitas-testserver"]
    
    
setup(
    name="levitas",
    version="0.0.1",
    description="A small wsgi framework",
    author="Tobias Weber",
    author_email="tobi-weber@gmx.de",
    url="",
    packages=["levitas",
              "levitas.middleware",
              "levitas.lib",
              "levitas.server"],
    scripts=scripts,
    long_description=""" A small wsgi framework """
)
