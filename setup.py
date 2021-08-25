'''
comic_html_view_generator
-------------------------

comic_html_view_generator is a command-line tool and library for creating
static HTML files for viewing comic books. Given a directory with images or
.cbz files in it, it'll create HTML files which embed those images in order,
and an overall "browse all the comics here" HTML page which will list all the
comics books which have had a readable HTML file generated from them.
'''

from setuptools import setup, find_packages
import ast
import re

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('comic_html_view_generator/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))

__license__ = 'GPLv3'

print(find_packages())
setup(
    name='comic_html_view_generator',
    version=version,
    url='https://github.com/lelandbatey/comic_html_view_generator',
    license=__license__,
    author='Leland Batey',
    author_email='lelandbatey@lelandbatey.com',
    description='HTML generator to view comic books',
    long_description=__doc__,
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Text Processing :: Markup :: HTML',
    ]
)
