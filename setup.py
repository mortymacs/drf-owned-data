"""Setup file."""
from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="owned_data",
    version="1.0.0",
    author="Morteza NourelahiAlamdari",
    author_email="m@0t1.me",
    description="data ownership library based on data columns (filter and permission)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/mortymacs/owned-data",
    project_urls={"Bug Tracker": "https://github.com/mortymacs/owned-data/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
)
