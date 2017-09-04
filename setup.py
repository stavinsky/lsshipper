import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n')
                for l in f if l.strip('\n') and not l.startswith('#')]


setup(
    name="lsshipper",
    version="0.0.1",
    author="Anton Stavinsky",
    author_email="stavinsky at gmail dot com",
    description=("Very basic python logstash shipper"),
    license="MIT",
    keywords="logstash filebeat",
    url="https://bitbucket.org/stavinsky/logstash_shipper",
    packages=find_packages(),
    tests_require=['pytest', 'pytest-asyncio', ],
    setup_requires=['pytest-runner', ],
    long_description=read('README.MD'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=parse_requirements("requirements.txt"),
)
