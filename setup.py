#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import os
import sys
from subprocess import Popen
from shutil import rmtree

from setuptools import Command, find_packages, setup
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
readme_files = ["README.md"]
for readme in readme_files:
    if os.path.exists(os.path.abspath(readme)):
        with open(os.path.join(here, readme), encoding="utf-8") as f:
            long_description = f.read()

scripts = []
for dirname, dirnames, filenames in os.walk("scripts"):
    for filename in filenames:
        scripts.append(os.path.join(dirname, filename))

# TODO: Simplify into a dict

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

# Define all install and test requirements
REQUIRED = ["argcomplete", "coloredlogs", "docker[tls]", "gTTS", "Markdown"]
SETUP_REQ = ["nose"]

REQUIRES_PYTHON = "~=3.6"
SCRIPTS = scripts
SOURCE = f"https://github.com/{GHUSERNAME}/markdown-to-speech/"
URL = f"https://github.com/{GHUSERNAME}/medium-to-speech"
VERSION = None

EXTRAS = {'testing': ["coverage", "flake8", "mock", "nose", "pytest"]}


# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


def _printer(msg, hashx=28):
    print("\n")
    print("#" * 80)
    print("#" * hashx, msg, "#" * hashx)
    print("#" * 80)
    print("\n")


def _post_install():
    cmd = "".join(SCRIPTS).split("/")[-1]
    _printer("Installation Complete!")
    print(f"If you would like tab-completion on {cmd}")
    print("Run the following commands in your terminal:\n")
    print("\t activate-global-python-argcomplete --user")
    print(f'\t eval "$(register-python-argcomplete {cmd})"')
    _printer("Done! ", 36)


class PostInstallCommand(install):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        atexit.register(_post_install)


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

        try:
            import twine
        except ImportError:
            errmsg = ("\n'Twine' is not installed.\n\nRun: \n\tpip install twine")
            self.status(errmsg)
            raise SystemExit(1)

        self.status("Building Source and Wheel (universal) distribution...")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")

        try:
            cmd = "twine test dist/*".split(" ")
            p = Popen(cmd, bufsize=-1)
            p.communicate()
            assert p.returncode == 0
        except AssertionError:
            self.status("Failed Twine Test.")
            raise

        try:
            self.status("Uploading the package to PyPI via Twine...")
            cmd = "twine upload dist/*".split()
            p = Popen(cmd, bufsize=-1)
            p.communicate()
        except AssertionError:
            self.status("Failed to upload to PyPi.")
            raise
        else:
            self.status("Pushing git tags...")
            os.system(f"git tag v{about.get('__version__')}")
            os.system("git push --tags")
            response = input("Do you want to generate a CHANGELOG.md? (y/n) ")
            if response.lower() == 'y':
                self.status("Generating the CHANGELOG.md.")
                os.system("make changelog")
            sys.exit(p.returncode)


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
    setup_requires=SETUP_REQ,
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
        "AboutMe": "https://blog.mphomphego.co.za/aboutme",
        "Donate!": f"https://paypal.me/mmphego",
    },
    cmdclass={"upload": UploadCommand, "install": PostInstallCommand},
    test_suite="tests"
)
