import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as readme:
    long_description = readme.read()

about = {}
with open(os.path.join(here, "glyculator", "__version__.py"), "r") as f:
    exec(f.read(), about)

packages = ["glyculator"]

setuptools.setup(
    name=about["__title__"],
    version = about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.5"
)