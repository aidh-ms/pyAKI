from setuptools import setup, find_packages

setup(
    pbr=True,
    packages=find_packages(),
    scripts=["bin/process_aki_stages"],
)
