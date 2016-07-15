# Copyright (c) 2016. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        "License :: OSI Approved :: Apache Software License",
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
