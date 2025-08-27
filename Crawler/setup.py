from setuptools import setup, find_packages

setup(
    name="web-crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.8.0',
        'beautifulsoup4>=4.11.0',
        'lxml>=4.9.0',
        'click>=8.1.0',
        'PyYAML>=6.0',
        'tqdm>=4.65.0',
        'loguru>=0.7.0',
    ],
    entry_points={
        'console_scripts': [
            'web-crawler=Crawler.cli:cli',
        ],
    },
)