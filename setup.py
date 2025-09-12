from setuptools import setup, find_packages

setup(
    name="ao3-client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rich"
    ],
    entry_points={
    "console_scripts": [
        "ao3=ao3.cli:main",
        ],
    },
    python_requires=">=3.9",
)
