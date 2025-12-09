"""
setup.py - setup script for dpm
"""

from setuptools import setup, find_packages

setup(
    name="dpm",
    version="1.0.0",
    description="Cross-language Dependency Package Manager",
    author="Yomna Hisham",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dpm=dpm.main:main",
        ],
    },
    python_requires=">=3.7",
    install_requires=[
        # no external dependencies - using only stdlib
    ],
)




