from setuptools import setup

setup(
    name='blackmamba',
    version='0.0.5',
    download_url = 'https://github.com/zrzka/blackmamba/archive/v0.0.5.tar.gz',
    
    description='Pythonista on steroids',
    
    url='https://github.com/zrzka/blackmamba',

    include_package_data = True,
    
    author='Robert Vojta',
    
    packages=[
        'blackmamba',
        'blackmamba.experimental'
    ],
    package_dir={'':'.'},

    keywords=['pythonista']
)

