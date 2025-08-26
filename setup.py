#!/usr/bin/env python3
"""
Setup script for Portal de Barrios Privados
Compatible with both setuptools and modern build systems
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Portal de Barrios Privados - Sistema de gestión integral"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="portalbarriosprivados",
    version="1.0.0",
    description="Portal de Barrios Privados - Sistema de gestión integral",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Manuel",
    author_email="manuel@example.com",
    url="https://github.com/manuel/portalbarriosprivados",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-flask>=1.3.0',
            'pytest-cov>=4.1.0',
            'pytest-json-report>=1.5.0',
            'factory-boy>=3.3.0',
            'faker>=19.12.0',
            'coverage>=7.3.2',
            'selenium>=4.15.2',
            'webdriver-manager>=4.0.1',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    entry_points={
        'console_scripts': [
            'portalbarriosprivados=main:main',
        ],
    },
    zip_safe=False,
)
