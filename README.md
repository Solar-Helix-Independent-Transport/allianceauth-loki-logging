# Alliance Auth Loki Logger

Python logging handler and formatter for [loki](https://grafana.com/oss/loki/)
for django. Supports blocking calls and non blocking ones, using threading.

Build on top of [django-loki-reloaded](https://github.com/zepc007/django-loki).

# Installation

Using pip:

```shell
pip install allianceauth-loki-logging
```

or

```shell
pip install git+https://github.com/Solar-Helix-Independent-Transport/allianceauth-loki-logging.git
```

# Usage

`LokiHandler` is a custom logging handler that pushes log messages to Loki.

Modify your settings to integrate `allianceauth-loki-logging` with Django's logging:

in your `local.py` add this at the end

```python
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
            'level': 'DEBUG',  # edit this line to change logging level to console
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
            'handlers': ['notifications'], ## untested need to test what this does
            'level': 'DEBUG',
        },
        'extensions': {
            'handlers': ['extension_file'], ## untested need to test what this does
            'level': 'DEBUG',
        }
    }
}

###  LOKI Specific settings
LOGGING['formatters']['loki'] = {
    'class': 'allianceauth-loki-logging.LokiFormatter'  # required
}

print(f"Configuring Loki Log job to: {os.path.basename(os.sys.argv[0])}")

LOGGING['handlers']['loki'] = {
    'level': 'DEBUG' if DEBUG else 'INFO',  # Required # We are auto setting the log level to only record debug when in debug.
    'class': 'allianceauth-loki-logging.LokiHandler',  # Required
    'formatter': 'loki',  #Required
    'timeout': 1,  # Post request timeout, default is 0.5. Optional
    # Loki url. Defaults to localhost. Optional.
    'url': 'http://localhost:3100/loki/api/v1/push',
    # Extra tags / labels to attach to the log. Optional, but usefull to differentiate instances.
    'tags': {"job":os.path.basename(os.sys.argv[0])}, # Auto set the job to differentiate between celery, gunicorn, manage.py etc.
    # Push mode. Can be 'sync' or 'thread'. Sync is blocking, thread is non-blocking. Defaults to sync. Optional.
    'mode': 'thread',
}

LOGGING['root'] = { # Set the root logger
    'handlers': ['loki', 'console'],
    'level': 'DEBUG' if DEBUG else 'INFO', # Auto set the log level to only record debug when in debug
}

WORKER_HIJACK_ROOT_LOGGER = False  # Do not overide with celery logging.
```

In your `supervisor.conf` update any workers to run at logging level DEBUG. `-l INFO`

```conf
....
command= celery -A myauth worker -l DEBUG
....
```
