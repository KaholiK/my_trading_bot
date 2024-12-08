# setup.py

from setuptools import setup, find_packages

setup(
    name='my_trading_bot',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List your dependencies here or ensure they're in requirements.txt
    ],
)
