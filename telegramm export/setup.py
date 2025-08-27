from setuptools import setup, find_packages

setup(
    name="telegramm_export",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Здесь должны быть зависимости из requirements.txt
        "psycopg2-binary",
        "python-telegram-bot",
        "aiohttp",
    ],
)