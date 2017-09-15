from setuptools import setup
import re

_init_py = open('blackmamba/__init__.py').read()
__version__ = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', _init_py).group(1)
__author__ = re.search(r'__author__\s*=\s*[\'"]([^\'"]*)[\'"]', _init_py).group(1)

setup(
    name='blackmamba',
    version=__version__,

    description='Pythonista on steroids',
    long_description=open('README.rst', 'rt').read(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: iOS',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development'
    ],

    url='https://github.com/zrzka/blackmamba',
    license='MIT',

    author=__author__,

    packages=[
        'blackmamba',
        'blackmamba.experimental',
        'blackmamba.project',
        'blackmamba.script'
    ],
    package_dir={'': '.'},

    keywords=['pythonista ios']
)
