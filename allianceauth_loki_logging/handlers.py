import atexit
import logging
import os
import queue
import sys
import threading
import time

import requests


def _write_stderr(message):
    # Write to the real stderr. sys.stderr may be redirected into logging
    # (celery does this), which would feed errors back into this handler.
    try:
        sys.__stderr__.write(message)
    except Exception:
        pass


class LokiHandler(logging.Handler):
    """
    Push log records to Loki.

    mode="thread" (default): emit() only enqueues; a single background thread
    per process batches and posts records. If Loki is slow or down, records
    are dropped once the queue is full rather than blocking the caller.

    mode="sync": post inline on every log call. Blocks the logging thread for
    up to `timeout` per record, not recommended for celery/gunicorn.
    """

    def __init__(
        self,
        timeout=0.5,
        url="http://localhost:3100/loki/api/v1/push",
        auth=None,
        tags={},
        mode="thread",
        max_queue_size=10000,
        batch_size=500,
        flush_interval=1.0,
    ):
        super(LokiHandler, self).__init__()

        self._url = url
        self._timeout = timeout
        self._auth = auth
        self._tags = tags
        self._mode = mode
        self._max_queue_size = max_queue_size
        self._batch_size = batch_size
        self._flush_interval = flush_interval

        self._pid = None
        self._queue = None
        self._thread = None
        self._session = None
        self._stop = threading.Event()
        self._start_lock = threading.Lock()
        self._dropped = 0
        self._last_error_report = 0

        atexit.register(self.close)

    def setFormatter(self, fmt):
        fmt.tags = self._tags

        self.formatter = fmt

    def emit(self, record):
        # Never log our own push activity (urllib3 / requests debug logs etc).
        if self._thread is not None and threading.current_thread() is self._thread:
            return

        try:
            payload = self.formatter.format(record)

            if self._mode == "sync":
                self._post(payload["streams"])
                return

            self._ensure_worker()
            try:
                self._queue.put_nowait(payload)
            except queue.Full:
                self._dropped += 1
        except Exception as e:
            self._report_error(f"Loki handler failed with: {e}\n")

    def _ensure_worker(self):
        # (Re)start the sender on first use and after fork, threads do not
        # survive a fork so each celery child needs its own.
        pid = os.getpid()
        if self._pid == pid:
            return
        with self._start_lock:
            if self._pid == pid:
                return
            self._queue = queue.Queue(maxsize=self._max_queue_size)
            self._session = requests.Session()
            self._stop = threading.Event()
            self._dropped = 0
            self._thread = threading.Thread(
                target=self._run, name="LokiHandler", daemon=True
            )
            self._thread.start()
            self._pid = pid

    def _run(self):
        while not self._stop.is_set():
            self._flush_batch(block=True)
        # Drain whatever is left on shutdown.
        while self._flush_batch(block=False):
            pass

    def _flush_batch(self, block):
        streams = []
        try:
            if block:
                streams.extend(self._queue.get(timeout=self._flush_interval)["streams"])
            while len(streams) < self._batch_size:
                streams.extend(self._queue.get_nowait()["streams"])
        except queue.Empty:
            pass

        if not streams:
            return False

        if self._dropped:
            dropped, self._dropped = self._dropped, 0
            self._report_error(f"Loki queue full, dropped {dropped} log records\n")

        self._post(streams)
        return True

    def _post(self, streams):
        try:
            sender = self._session if self._session is not None else requests
            response = sender.post(
                self._url,
                json={"streams": streams},
                timeout=self._timeout,
                auth=self._auth,
            )
            if response.status_code != 204:
                self._report_error(
                    f"Got status {response.status_code} from loki with message: {response.text}\n"
                )
        except requests.exceptions.Timeout:
            self._report_error("Loki connection timed out\n")
        except Exception as e:
            self._report_error(f"Loki connection failed with: {e}\n")

    def _report_error(self, message):
        # Rate limit so a dead Loki doesn't flood stderr.
        now = time.monotonic()
        if now - self._last_error_report >= 10:
            self._last_error_report = now
            _write_stderr(message)

    def close(self):
        if self._thread is not None and self._pid == os.getpid() and self._thread.is_alive():
            self._stop.set()
            self._thread.join(timeout=max(self._timeout * 2, 1))
        super(LokiHandler, self).close()
