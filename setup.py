from setuptools import setup, find_packages
from os import path as pth
import ast
import re


def _read(fname):
    return open(pth.join(pth.dirname(__file__), fname)).read()


# Derive our version number from the version number definited in pyproject.toml
_version_re = re.compile(r'version\s+=\s+(.*)')
with open('pyproject.toml', 'rb') as f:
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
    long_description=_read('README.rst'),
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
    ],
    entry_points={
        'console_scripts': ['comic_html_view_generator=comic_html_view_generator.chvg:main']
    }
)
