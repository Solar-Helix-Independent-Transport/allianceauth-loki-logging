# Django-loki Reloaded

Python logging handler and formatter for [loki](https://grafana.com/oss/loki/)
for django.  Supports blocking calls and non blocking ones, using threading.

Builds on top of [django-loki](https://github.com/zepc007/django-loki).

# Installation

Using pip:

```shell
pip install django-loki-reloaded
```

# Usage

`LokiHandler` is a custom logging handler that pushes log messages to Loki.

Modify your `settings.py` to integrate `django-loki-reloaded` with Django's logging:

```python
LOGGING = {
    'formatters': {
        'loki': {
            'class': 'django_loki.LokiFormatter',  # required
        },
    },
    'handlers': {
        'loki': {
            'level': 'DEBUG',  # Log level. Required
            'class': 'django_loki.LokiHttpHandler',  # Required
            'formatter': 'loki',  # Loki formatter. Required
            'timeout': 0.5,  # Post request timeout, default is 0.5. Optional
            'url': 'http://localhost:3100/loki/api/v1/push',  # Loki url. Defaults to localhost. Optional.
            'auth': ("user", "password"),  # Basic auth to authenticate with loki. Default is None (i.e. no auth). Optional
            'tags': {"foo": "bar"},  # Tags / Labels to attach to the log. Optional, but strongly encoraged to use.
            'mode': 'thread',  # Push mode. Can be 'sync' or 'thread'. Sync is blocking, thread is non-blocking. Defaults to sync. Optional.
        },
    },
    'loggers': {
        'django': {
            'handlers': ['loki'],
            'level': 'INFO',
        }
    },
}
```
