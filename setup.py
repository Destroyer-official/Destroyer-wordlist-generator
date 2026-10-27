from setuptools import setup, find_packages

setup(
    name="destroyer-wordlist-generator",
    version="3.0.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "destroyer = destroyer.cli:main",
        ],
    },
    python_requires=">=3.8",
)
