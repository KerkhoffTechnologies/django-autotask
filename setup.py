#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = (1, 19, 0)

project_version = '.'.join(map(str, VERSION))

LONG_DESCRIPTION = open('README.md', encoding="utf-8").read()

setup(
    name='django-autotask',
    version=project_version,
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
    python_requires='>=3.12',
    install_requires=[
        'requests',
        'django>=4.2',
        'python-dateutil',
        'django-model-utils',
        'django-braces',
        'django-extensions',
        'retrying',
    ],
    # Django likes to inspect apps for /migrations directories, and can't if
    # package is installed as a egg. zip_safe=False disables installation as
    # an egg.
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.2',
        'Framework :: Django :: 6.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Development Status :: 1 - Planning',
    ],
)
