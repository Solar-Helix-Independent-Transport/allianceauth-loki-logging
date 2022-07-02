import logging
import socket
from datetime import datetime
from logging import BASIC_FORMAT

import pytz


class LokiFormatter(logging.Formatter):
    asctime_search = "%(asctime)"
    tz = "UTC"
    source = "Loki"
    src_host = "localhost"
    tags = {}

    def __init__(self, fmt, dfmt, style, fqdn=False):
        super(LokiFormatter, self).__init__()

        self.fmt = fmt or BASIC_FORMAT
        self.dfmt = dfmt or "%Y-%m-%d %H:%M:%S"
        self.style = style
        if fqdn:
            self.host = socket.getfqdn()
        else:
            self.host = socket.gethostname()

    def format_timestamp(self, time):
        return datetime.fromtimestamp(time, tz=pytz.timezone(self.tz))

    def usesTime(self):
        return self.fmt.find(self.asctime_search) >= 0

    def formatMessage(self, record):
        try:
            return self.fmt % record.__dict__
        except KeyError as e:
            raise ValueError("Formatting field not found in record: %s" % e)

    def format(self, record):
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.dfmt)

        message = self.formatMessage(record)

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if message[-1:] != "\n":
                message = message + "\n"
            message = message + record.exc_text

        if record.stack_info:
            if message[-1:] != "\n":
                message = message + "\n"

            message = message + self.formatStack(record.stack_info)

        message = {
            "streams": [
                {
                    "stream": {
                        **self.tags,
                    },
                    "values": [
                        [
                            self.format_timestamp(record.created),
                            message,
                        ]
                    ],
                }
            ]
        }

        return message
