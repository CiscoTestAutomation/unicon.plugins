#! /usr/bin/env python

'''Setup file for Unicon Plugins

See:
    https://packaging.python.org/en/latest/distributing.html
'''


from ciscodistutils import setup, find_packages, is_devnet_build
from ciscodistutils.tools import read, version_info
from ciscodistutils.common import (AUTHOR,
                                   URL,
                                   CLASSIFIERS,
                                   SUPPORT,
                                   LICENSE)

# compute version range
version, version_range = version_info('src', 'unicon_plugins', '__init__.py')

install_requires = ['setuptools',
                    'pyyaml',
                    'dill',
                    'unicon {range}'.format(range = version_range)],

# launch setup
setup(
    name = 'unicon_plugins',
    version = version,

    # descriptions
    description = 'Unicon Connection Library Plugins',
    long_description = read('DESCRIPTION.rst'),

    # the project's main homepage.
    url = URL,

    # author details
    author = AUTHOR,
    author_email = SUPPORT,

    # project licensing
    license = LICENSE,

    # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = CLASSIFIERS,

    # project keywords
    keywords = 'unicon connection pyats cisco',

    # project packages
    packages = find_packages(where = 'src'),

    # project directory
    package_dir = {
        '': 'src',
    },

    # additional package data files that goes into the package itself
    package_data = {'': ['README.rst',
                         'tests/mock_data/*/*.yaml',
                         'tests/mock_data/*/*.txt',
                         'tests/mock_data/*/*/*.txt',
                         'tests/unittest/ssh_host_key',
                         ]},

    # Standalone scripts
    scripts = [
    ],

    # package dependencies
    install_requires = install_requires,

    # any additional groups of dependencies.
    # install using: $ pip install -e .[dev]
    #
    # NOTE: asyncssh is also a dev dependency needed to run unit test,
    # but is left off the list to allow continued python 3.4 support.
    extras_require = {
        'robot': ['robotframework'],
        'pyats': ['pyats' if is_devnet_build() else 'ats'],
        'dev': ['cisco-distutils',
                'coverage',
                'restview',
                'Sphinx',
                'sphinxcontrib-napoleon',
                'sphinxcontrib-mockautodoc',
                'sphinx-rtd-theme'],
    },

    # any data files placed outside this package.
    # See: http://docs.python.org/3.4/distutils/setupscript.html
    # format:
    #   [('target', ['list', 'of', 'files'])]
    # where target is sys.prefix/<target>
    data_files = [],

    # non zip-safe (never tested it)
    zip_safe = False,
)
