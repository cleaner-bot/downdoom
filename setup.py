from setuptools import find_namespace_packages, setup  # type: ignore

setup(
    name="downdoom",
    version="0.1.1",
    url="https://github.com/cleaner-bot/downdoom",
    author="Leo Developer",
    author_email="git@leodev.xyz",
    description="down detector",
    packages=find_namespace_packages(include=["downdoom*"]),
    package_data={"downdoom": ["py.typed"]},
)
