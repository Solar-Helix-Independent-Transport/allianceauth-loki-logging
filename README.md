# Alliance Auth Loki Logger

Python logging handler and formatter for [loki](https://grafana.com/oss/loki/)
for django. Supports blocking calls and non blocking ones, using threading.

Build on top of [django-loki-reloaded](https://github.com/zepc007/django-loki).

# Why?

A single location for all logs across auth, Separate to auth! With search and notifications etc. Complete with python trace type data for everything.

![Logs 1](https://i.imgur.com/rYUsSDy.png)

![Logs 2](https://i.imgur.com/maTS2qQ.png)

![Logs 3](https://i.imgur.com/YS5pJiX.png)

# Installation

Have a [loki instance configured and running](https://github.com/grafana/loki)

### Bare Metal:

```shell
pip install allianceauth-loki-logging
```

or

```shell
pip install git+https://github.com/Solar-Helix-Independent-Transport/allianceauth-loki-logging.git
```

### Docker

add this to your requirements file and rebuild your image

```
allianceauth-loki-logging>=1.0.0
```

or

```
allianceauth-loki-logging @ git+https://github.com/Solar-Helix-Independent-Transport/allianceauth-loki-logging.git
```

# Usage

`LokiHandler` is a custom logging handler that pushes log messages to Loki.

Modify your settings to integrate `allianceauth_loki_logging` with Django's logging:

in your `local.py` add this at the end, Be sure to read the comments and update any that need to be updated. Specifically the url for loki.

```python
LOKI_URL = "'http://loki:3100/loki/api/v1/push'
### Override the defaults from base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'extension_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/extensions.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # edit this line to change max log file size
            'backupCount': 5,  # edit this line to change number of log backups
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',  # edit this line to change logging level to console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'notifications': {  # creates notifications for users with logging_notifications permission
            'level': 'ERROR',  # edit this line to change logging level to notifications
            'class': 'allianceauth.notifications.handlers.NotificationHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'allianceauth': {
            'handlers': ['notifications'],
            'level': 'ERROR',
        },
        'extensions': {
            'handlers': ['extension_file'], 
            'level': 'DEBUG' if DEBUG else 'INFO',
        }
    }
}

###  LOKI Specific settings
LOGGING['formatters']['loki'] = {
    'class': 'allianceauth_loki_logging.LokiFormatter'  # required
}

print(f"Configuring Loki Log job to: {os.path.basename(os.sys.argv[0])}")

LOGGING['handlers']['loki'] = {
    'level': 'DEBUG' if DEBUG else 'INFO',  # Required # We are auto setting the log level to only record debug when in debug.
    'class': 'allianceauth_loki_logging.LokiHandler',  # Required
    'formatter': 'loki',  #Required
    'timeout': 1,  # Post request timeout, default is 0.5. Optional
    # Loki url. Defaults to localhost. Optional.
    'url': , LOKI_URL,
    # Extra tags / labels to attach to the log. Optional, but usefull to differentiate instances.
    'tags': {
        "job":os.path.basename(os.sys.argv[0]), # Auto set the job to differentiate between celery, gunicorn, manage.py etc.
        # you could add extra tags here if you were running multiple auths and needed to be able to tell them apart in a single loki instance eg:
        # "auth": "CoolAuth 1",
    }, 
    # Push mode. Can be 'sync' or 'thread'. Sync is blocking, thread is non-blocking. Defaults to sync. Optional.
    'mode': 'thread',
}

LOGGING['root'] = { # Set the root logger
    'handlers': ['loki', 'console'],
    'level': 'DEBUG' if DEBUG else 'INFO', # Auto set the log level to only record debug when in debug
}

WORKER_HIJACK_ROOT_LOGGER = False  # Do not overide with celery logging.
```

## Diagnosing issues with logs not being pushed in HIGHLY threaded environments

add the following to your loki config to bypass the rate limits.

```yaml
limits_config:
  max_streams_per_user: 0
  max_global_streams_per_user: 0
```