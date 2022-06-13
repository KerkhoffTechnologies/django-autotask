#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import djautotask

LONG_DESCRIPTION = open('README.md', encoding="utf-8").read()

setup(
    name='django-autotask',
    version=djautotask.__version__,
    description='Django app for working with Autotask. '
                'Defines models (tickets, members, companies, etc.) '
                'and callbacks.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords='django autotask rest api python',
    packages=find_packages(),
    author='Kerkhoff Technologies Inc.',
    author_email='matt@kerkhofftech.ca',
    url="https://github.com/KerkhoffTechnologies/django-autotask",
    include_package_data=True,
    license='MIT',
    install_requires=[
        'requests',
        'django',
        'python-dateutil',
        'django-model-utils',
        'django-braces',
        'django-extensions',
        'retrying',
    ],
    test_suite='runtests.suite',
    tests_require=[
        'responses',
        'model-mommy',
        'django-coverage',
        'names'
    ],
    # Django likes to inspect apps for /migrations directories, and can't if
    # package is installed as a egg. zip_safe=False disables installation as
    # an egg.
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Development Status :: 1 - Planning',
    ],
)
