import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'bcrypt',
    'coloredlogs',
    'lxml',
    'mako>=0.7.0',
    'pyramid',
    'pyramid_beaker',
    'pyramid_debugtoolbar',
    'pyramid_scss',
    'pyramid_tm',
    'pytz',
    'simplejson',
    'sqlalchemy',
    'transaction',
    'tzlocal',
    'waitress',
    'whoosh',
    'zope.sqlalchemy',
]

# pypi versions of stdlib packages
if sys.version_info < (3, 4):
    requires.append('pathlib')

setup(
    name='spline',
    version='0.0',
    description='spline',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='spline',

    install_requires=requires,
    entry_points="""\
        [paste.app_factory]
        main = spline.app:main
    """,
)
