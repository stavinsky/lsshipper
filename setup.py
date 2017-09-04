import os
from setuptools import setup, find_packages
import pypandoc


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n')
                for l in f if l.strip('\n') and not l.startswith('#')]


setup(
    name="lsshipper",
    version="0.1.1",
    author="Anton Stavinsky",
    author_email="stavinsky@gmail.com",
    description=("Very basic python logstash shipper"),
    license="MIT",
    keywords="logstash filebeat",
    url="https://github.com/stavinsky/lsshipper/",
    packages=find_packages(exclude=['tests*']),
    tests_require=['pytest', 'pytest-asyncio', ],
    setup_requires=['pytest-runner', ],
    long_description=pypandoc.convert('README.md', 'rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        'console_scripts': [
            'lsshipper = lsshipper.start:main'
            ]
        },
    python_requires='>=3.5'
)
