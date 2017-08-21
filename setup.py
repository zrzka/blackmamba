from setuptools import setup

setup(
    name='blackmamba',
    version='0.0.4',
    download_url = 'https://github.com/zrzka/blackmamba/archive/v0.0.4.tar.gz',
    
    description='Pythonista on steroids',
    
    url='https://github.com/zrzka/blackmamba',
    
    author='Robert Vojta',
    
    packages=[
        'blackmamba',
        'blackmamba.experimental'
    ],
    package_dir={'':'.'},

    keywords=['pythonista']
)

