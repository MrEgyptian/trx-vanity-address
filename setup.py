#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trx-vanity-address",
    version="1.0.0",
    author="TRX靓号生成器",
    author_email="",
    description="TRX靓号地址生成器 - 使用GPU加速生成包含连续相同数字的TRX地址",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trx-vanity-address",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "trx-vanity=trx_vanity_address:main",
        ],
    },
    keywords="trx, vanity, address, cryptocurrency, blockchain, gpu",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/trx-vanity-address/issues",
        "Source": "https://github.com/yourusername/trx-vanity-address",
        "Documentation": "https://github.com/yourusername/trx-vanity-address#readme",
    },
) 