#!/usr/bin/env python3
"""
REDLINE Setup Configuration
Package distribution setup for PyPI
"""

from setuptools import setup, find_packages
import os

# Read the requirements file
def read_requirements():
    """Parse requirements.txt and return list of dependencies."""
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

# Read the long description from README
def read_long_description():
    """Read README.md for PyPI long description."""
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "REDLINE - Professional Financial Data Analysis Platform"

setup(
    name="redline-financial",
    version="1.0.0",
    author="REDLINE Development Team",
    author_email="support@redline.example.com",
    description="Professional financial data analysis platform with GUI and web interface",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/keepdevops/redline2",
    project_urls={
        "Bug Tracker": "https://github.com/keepdevops/redline2/issues",
        "Documentation": "https://github.com/keepdevops/redline2/blob/main/README.md",
        "Source Code": "https://github.com/keepdevops/redline2",
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'build', 'dist']),
    py_modules=['main', 'web_app'],
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.11',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Flask",
    ],
    entry_points={
        'console_scripts': [
            'redline-gui=main:main',
            'redline-web=web_app:main',
            'redline=redline.cli.download:main',
        ],
    },
    package_data={
        'redline.web': [
            'static/**/*',
            'templates/**/*',
        ],
        'redline': [
            'data_config.ini',
        ],
    },
    keywords=[
        'finance',
        'stock',
        'trading',
        'analysis',
        'data',
        'yfinance',
        'financial-data',
        'stock-market',
        'investment',
        'portfolio',
    ],
    zip_safe=False,
)
