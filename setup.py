#!/usr/bin/env python3
"""
Setup script for Congressional Election Simulation.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="congressional-election-sim",
    version="1.0.0",
    author="Election Simulation Project",
    description="Simulates congressional elections using ranked choice voting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python_election_sim",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Sociology",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.4.0",
        "numpy>=1.21.0,<2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "election-sim=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json"],
    },
)

