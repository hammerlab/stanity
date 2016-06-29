try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import versioneer

setup(
    name="stanity",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jacki Buros and Tim O'Donnell",
    author_email="timodonnell@gmail.com",
    packages=["stanity"],
    url="https://github.com/hammerlab/stanity",
    license="Apache License",
    description="Helper library for working with Stan models in Python",
    long_description=open('README.rst').read(),
    download_url='https://github.com/hammerlab/stanity/tarball/%s' % versioneer.get_version(),
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
        "matplotlib",
    "numpy",
    ],
)
