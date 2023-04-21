import logging
import sys
from threading import Thread

import requests


class LokiHandler(logging.Handler):
    def __init__(
        self,
        timeout=0.5,
        url="http://localhost:3100/loki/api/v1/push",
        auth=None,
        tags={},
        mode="sync",
    ):
        super(LokiHandler, self).__init__()

        self._url = url
        self._timeout = timeout
        self._auth = auth
        self._tags = tags

        self._mode = mode

    def emit(self, record):
        try:
            payload = self.formatter.format(record)

            _push_message(
                self._url, json=payload, timeout=self._timeout, auth=self._auth
            )
        except requests.exceptions.ReadTimeout:
            sys.stderr.write("Loki connection timed out\n")
        except Exception as e:
            sys.stderr.write(f"Loki connection failed with: {e}\n")

    def setFormatter(self, fmt):
        fmt.tags = self._tags

        self.formatter = fmt

    def _push_message(self, *args, **kwargs):
        if self._mode == "sync":
            return _push_message(*args, **kwargs)

        if self._mode == "thread":
            return Thread(target=_push_message, args=args, kwargs=kwargs).start()


def _push_message(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    #print(response)
    if response.status_code != 204:
        sys.stderr.write(
            f"Got status {response.status_code} from loki with message: {response.text}\n"
        )
