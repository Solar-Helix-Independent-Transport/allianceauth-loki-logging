"""
MIT License

Copyright (c) 2021 Zepc Myers, 2022 h3nnn4n (Renan S Silva)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
"""

from .handlers import LokiHandler
from .formatters import LokiFormatter

__all__ = ['LokiHandler', 'LokiFormatter']
__version__ = "1.0.3"
name = "django_loki_reloaded"
