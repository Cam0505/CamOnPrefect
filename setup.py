# setup.py
from setuptools import setup, find_packages

setup(
    name="camonprefect",
    version="0.1",
    packages=find_packages(),
    package_data={"camonprefect": ["dbt/*", "pipelines/*"]}
)
