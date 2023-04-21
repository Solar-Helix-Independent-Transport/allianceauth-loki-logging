from setuptools import setup

setup(
    name='allianceauth-loki-logging',
    version='0.0.1',
    packages=['allianceauth-loki-logging'],
    url='https://github.com/h3nnn4n/django-loki-reloaded',
    license='MIT',
    author='aaronkable',
    author_email='aaronkable@gmail.com',
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
