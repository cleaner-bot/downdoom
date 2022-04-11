from setuptools import setup, find_namespace_packages  # type: ignore

setup(
    name="downdoom",
    version="0.1.0",
    url="https://github.com/cleaner-bot/downdoom",
    author="Leo Developer",
    author_email="git@leodev.xyz",
    description="down detector",
    packages=find_namespace_packages(include=["downdoom*"]),
    package_data={"downdoom": ["py.typed"]},
)
