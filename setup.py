from setuptools import setup, find_packages

setup(name='sfordata',
    version='0.0.1',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'sforparser = sfordata.cli.parser:main',
        ],
        'sfordata.parser': [
            'apd = sfordata.parser.apd:ApdParser',
        ],
    },
)
