import logging
import sys

import requests


class LokiHandler(logging.Handler):
    def __init__(
        self,
        host="localhost",
        port=3100,
        timeout=0.5,
        protocol="http",
        source="Loki",
        src_host="localhost",
        auth=None,
        tz="UTC",
    ):
        super(LokiHandler, self).__init__()

        self._address = f"{protocol}://{host}:{port}"
        self._post_address = f"{self._address}/api/prom/push"
        self._tz = tz
        self._timeout = timeout
        self._source = source
        self._src_host = src_host
        self._auth = auth

    def emit(self, record):
        try:
            payload = self.formatter.format(record)

            res = requests.post(
                self._post_address, json=payload, timeout=self._timeout, auth=self._auth
            )

            if res.status_code != 204:
                sys.stderr.write("Loki occurs errors\n")
        except requests.exceptions.ReadTimeout:
            sys.stderr.write("Loki connect time out\n")
        except Exception:
            sys.stderr.write(f"{record.getMessage()}\n")

    def setFormatter(self, fmt):
        fmt.tz = self._tz
        fmt.source = self._source
        fmt.src_host = self._src_host

        self.formatter = fmt
