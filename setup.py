from setuptools import setup, find_packages

setup(
    name="fakit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "GitPython>=3.1.0",
        "faker>=37.5.3",
        "markovify>=0.9.4"
    ],
    entry_points={
        "console_scripts": [
            "fakit=fakit.cli:main"
        ]
    },
    python_requires=">=3.8",
)
