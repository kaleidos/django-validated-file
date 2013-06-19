#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'django-validated-file',
    version = ":versiontools:validatedfile:",
    description = "This Django app adds a new field type, ValidatedFileField, that add the capability of checking the document size and types the user may send.",
    long_description = "",
    keywords = 'django, filefield, validation',
    author = u'Andrés Moya Velázquez',
    author_email = 'andres.moya@kaleidos.net',
    url = 'https://github.com/kaleidos/django-validated-file',
    license = 'GPL3',
    include_package_data = True,
    package_data = {
        '': ['*.po', '*.mo'],
    },
    packages = find_packages(),
    install_requires=[
        'distribute',
        'python-magic >= 0.4.2',
    ],
    setup_requires = [
        'versiontools >= 1.8',
        'python-magic >= 0.4.2',
    ],
    classifiers = [
        "Programming Language :: Python",
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
