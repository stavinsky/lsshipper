import os
from setuptools import setup, find_packages
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst').replace("\r", "")
except ImportError:
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        long_description = f.read()


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n')
                for l in f if l.strip('\n') and not l.startswith('#')]


setup(
    name="lsshipper",
    version="0.1.8",
    author="Anton Stavinsky",
    author_email="stavinsky@gmail.com",
    description=("Very basic python logstash shipper"),
    license="MIT",
    keywords="logstash filebeat",
    url="https://github.com/stavinsky/lsshipper/",
    packages=find_packages(exclude=['tests*']),
    tests_require=['pytest', 'pytest-asyncio', ],
    setup_requires=['pytest-runner', ],
    long_description=long_description,
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
    python_requires='>=3.5',
    data_files=[
        ('', ['README.md']),
        ('', ['requirements.txt'])
    ],
)
