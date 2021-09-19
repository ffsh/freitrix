from setuptools import setup

setup(
    name='synman',
    version='0.1.0',
    py_modules=['synman'],
    install_requires=[
        'Click',
        'Tabulate',
        'Requests',
        'humanize'
    ],
    entry_points={
        'console_scripts': [
            'synman = synman.synman:cli',
        ],
    },
)