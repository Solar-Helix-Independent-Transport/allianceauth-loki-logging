# Django-loki

Python logging handler and formatter for [loki](https://grafana.com/oss/loki/) for django

# Installation

Using pip:

```shell
pip install django-loki-reloaded
```

# Usage

`LokiHandler` is a custom logging handler which sends Loki-messages using `http` or `https`.

Modify your `settings.py` to integrate `django-loki` with Django's logging:

```python
LOGGING = {
    ...
    'formatters': {
        'loki': {
            'class': 'django_loki.LokiFormatter',  # required
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] [%(funcName)s] %(message)s',  # optional, default is logging.BASIC_FORMAT
            'datefmt': '%Y-%m-%d %H:%M:%S',  # optional, default is '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'loki': {
            'level': 'DEBUG',  # required
            'class': 'django_loki.LokiHttpHandler',  # required
            'host': '192.168.57.242',  # required, your grafana/Loki server host, e.g:192.168.57.242.
            'formatter': 'loki',  # required, loki formatter,
            'port': 3100,  # optional, your grafana/Loki server port, default is 3100
            'timeout': 0.5,  # optional, request Loki-server by http or https time out, default is 0.5
            'protocol': 'http',  # optional, Loki-server protocol, default is http
            'source': 'Loki',  # optional, label name for Loki, default is Loki
            'src_host': 'localhost',  # optional, label name for Loki, default is localhost
            'tz': 'UTC',  # optional, timezone for formatting timestamp, default is UTC, e.g:Asia/Shanghai
        },
    },
    'loggers': {
        'django': {
            'handlers': ['loki'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}
```
