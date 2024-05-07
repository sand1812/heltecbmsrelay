#!/usr/bin/python3
import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="heltecbmsrelay",
    version="0.1.0",
    description="Client for Heltec BMS with relay output",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sand1812/heltecbmsrelay.git",
    author="Greg Giannoni",
    author_email="greg@wootech.art",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["heltecbmsrelay"],
    install_requires=['bleak>=0.21',],
    entry_points={"console_scripts": ["heltecbms=heltecbmsrelay:main"]},
)
