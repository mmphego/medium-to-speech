#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get the pip requirements from the pip-requirements file
with open(os.path.join(here, "pip-requirements.txt"), encoding="utf-8") as _f:
    pip_req = [pkg.strip() for pkg in _f.readlines()]

scripts = []
for dirname, dirnames, filenames in os.walk("scripts"):
    for filename in filenames:
        scripts.append(os.path.join(dirname, filename))

# Package meta-data.
AUTHOR = "Mpho Mphego"
AUTHOR_EMAIL = "mpho112@gmail.com"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]
DESCRIPTION = "Medium posts as Markdown to Speech."
GHUSERNAME = "mmphego"
KEYWORDS = " medium markdown docker-py text-to-speech"
LICENSE = "MIT"
LONG_DESCRIPTION = long_description
NAME = "medium-speech"
REQUIRED = pip_req
REQUIRES_PYTHON = ">=3.6.0"
SCRIPTS = scripts
SOURCE = f"https://github.com/{GHUSERNAME}/markdown-speech/"
URL = f"https://github.com/{GHUSERNAME}/medium-to-speech"
VERSION = None

EXTRAS = {}

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds...")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution...")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")

        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")

        self.status("Pushing git tags...")
        os.system(f"git tag v{about['__version__']}")
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    scripts=SCRIPTS,
    project_urls={
        "Bug Reports": SOURCE + "/issues",
        "Source": SOURCE,
        "Say Thanks!": f"https://saythanks.io/to/{GHUSERNAME}",
    },
    cmdclass={"upload": UploadCommand},
)
