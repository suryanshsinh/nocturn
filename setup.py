from setuptools import setup, find_packages

setup(
    name="nocturn",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mnemonic==0.20",
        "eth-account==0.6.0",
        "solana==0.23.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
