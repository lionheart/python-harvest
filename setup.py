from setuptools import setup, find_packages
import sys, os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='Harvest Time Tracking API Client',
    version=read('VERSION'),
    description="Harvest api client",
    long_description=read('README'),
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        ],
    keywords='harvestapp timetracking api',
    author='Alex Goretoy',
    author_email='alex@goretoy.com',
    url='https://github.com/aurorasoftware/python-harvest',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=read("requirements.txt").split("\n")
)
