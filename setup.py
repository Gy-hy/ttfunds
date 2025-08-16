from setuptools import setup, find_packages

setup(
    name="ttfunds",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "aiosqlite",
        "pandas",
        "matplotlib",
        "tqdm"
    ],
)