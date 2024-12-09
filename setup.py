# setup.py

from setuptools import setup, find_packages

setup(
    name='my_trading_bot',
    version='1.0.0',
    author=kaholik,  # Replace with your actual name
    author_email=kaholisk@gmail.com,  # Replace with your actual email
    description='A powerful AI-driven trading bot with web access, continuous learning, and strategy generation using OpenAI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=https://github.com/KaholiK/my_trading_bot.git,  # Replace with your GitHub repo URL
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'python-dotenv',
        'openai',
        'pandas',
        'torch',
        'pytest',
        'pytest-cov',
        'fastapi',
        'uvicorn',
        'requests',
        'APScheduler',
        'numpy',
        'alpaca-trade-api',
        'prometheus_client',
        'beautifulsoup4',  # For web scraping
        'selenium',         # If needed for dynamic content
        'scikit-learn',    # For additional ML algorithms
    ],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',  # Replace if using a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
