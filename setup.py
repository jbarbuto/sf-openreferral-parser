from setuptools import setup, find_packages

setup(name='sforparser',
    version='0.0.1',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'sforparser = sforparser.cli:main',
        ],
        'sforparser.parser': [
            'apd = sforparser.parser.apd:ApdParser',
        ],
    },
)
