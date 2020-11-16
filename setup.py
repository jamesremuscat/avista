from setuptools import setup, find_packages
import re

VERSIONFILE = "src/avista/_version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
except EnvironmentError:
    print("unable to find version in %s" % (VERSIONFILE,))
    raise RuntimeError("if %s exists, it is required to be well-formed" % (VERSIONFILE,))

setup(
    name='avista',
    version=verstr,
    description='Library for controlling A/V devices',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/avista',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir={'': 'src'},
    long_description="""\
    avista is a library for controlling A/V devices such as video switchers. It
    is a modernised rewrite of the avx library from the same author.
    """,
    setup_requires=[],
    tests_require=[],
    install_requires=[
        'autobahn[twisted]',
        'pyserial',
        'recordclass'
    ],
    entry_points={
        'console_scripts': [
        ],
    }
)
