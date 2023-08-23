# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

PACKAGE_NAME = "ReconRaccoon"
VERSION = "1.0.1"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        author="whatev33r",
        description="Web Security Testing Framework",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/whatev33r/ReconRaccoon",
        scripts=[
            "ReconRaccoon/ReconRaccoon.py",
        ],
        python_requires='>=3'
    )
