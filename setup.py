from setuptools import setup, find_namespace_packages

setup(
    name='avista',
    use_scm_version=True,
    description='Library for controlling A/V devices',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/avista',
    packages=find_namespace_packages('src', exclude=["*.tests"]),
    package_dir={'': 'src'},
    long_description="""\
    avista is a library for controlling A/V devices such as video switchers. It
    is a modernised rewrite of the avx library from the same author.
    """,
    setup_requires=['setuptools_scm'],
    tests_require=[],
    install_requires=[
        'autobahn[serialization,twisted]',
        'construct',
        'mido',
        'netaudio==0.0.10',
        'pyserial',
        'ratelimiter==1.2.0.post0',
        'recordclass',
        'throttle',
        'treq'
    ],
    entry_points={
        'console_scripts': [
            'avista-device=avista.runner:run'
        ],
    }
)
