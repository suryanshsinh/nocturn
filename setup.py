from setuptools import setup, find_packages

setup(
    name="nocturn",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mnemonic",
        "eth-account",
        "web3",
        "bip32utils",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
