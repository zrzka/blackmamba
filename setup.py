from setuptools import setup

setup(
    name='blackmamba',
    version='0.0.1',
    
    description='Pythonista on steroids',
    
    url='https://github.com/zrzka/blackmamba',
    
    author='Robert Vojta',
    
    license='The Unlicense',
    
    packages=[
        'blackmamba',
        'blackmamba.experimental'
    ],
    package_dir={'':'.'}
)

