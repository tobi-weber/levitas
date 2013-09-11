# -*- coding: utf-8 -*-

"""
This is a basic wsgi script.
"""

import os
os.environ["LEVITAS_SETTINGS"] = "biballigare.example_settings"

from levitas.handler import WSGIHandler
application = WSGIHandler()
