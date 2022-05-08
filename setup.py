from setuptools import setup, find_packages

from unredoable import __version__


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='unredoable',
    packages=find_packages(exclude=(["tests"])),
    version=__version__,
    license='MIT',
    description='Provision of object-specific undoing and redoing functionality through wrapper class',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['singleton', 'borg', 'design-patterns'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url='https://github.com/w2sv/unredoable',
    python_requires='>=3.6',
    author='w2sv',
    author_email='zangenbergjanek@googlemail.com',
    platforms=['Linux', 'Windows', 'MacOS']
)