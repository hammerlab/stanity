try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.2.1"

setup(
    name="stanity",
    version=version,
    author="Jacki Buros and Tim O'Donnell",
    author_email="timodonnell@gmail.com",
    packages=["stanity"],
    url="https://github.com/hammerlab/stanity",
    license="Apache License",
    description="Helper library for working with Stan models in Python",
    long_description=open('README.rst').read(),
    download_url='https://github.com/hammerlab/stanity/tarball/%s' % version,
    entry_points={
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache 2 License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        "pystan",
        "nose",
        "typechecks",
        "future>=0.14.3",
        "pandas",
        "seaborn",
    ],
    dependency_links=[
        "https://raw.githubusercontent.com/avehtari/PSIS/master/py/psis.py"
    ],
)
