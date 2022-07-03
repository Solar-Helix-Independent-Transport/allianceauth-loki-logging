from setuptools import setup

setup(
    name='django-loki-reloaded',
    version='1.0.0',
    packages=['django_loki_reloaded'],
    url='https://github.com/h3nnn4n/django-loki-reloaded',
    license='MIT',
    author='h3nnn4n',
    author_email='django_loki_reloaded@h3nnn4n.me',
    description='A non-blocking django logging handler for Loki',
    keywords=['python', 'loki', 'grafana', 'logging', 'metrics', 'threaded'],
    install_requires=[
        'requests',
        'pytz',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        "Environment :: Web Environment",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
