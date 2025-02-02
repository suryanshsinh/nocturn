from setuptools import setup, find_packages

setup(
    name="nocturn",
    version="0.1.4",
    author="Suryanshsinh Sisodiya",
    author_email="suryanshsinhsisodiya@gmail.com",
    description="A Python-based lightweight crypto wallet for Ethereum, Binance Smart Chain, and Polygon.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/suryanshsinh/nocturn",
    packages=find_packages(),
    install_requires=[
        "web3",
        "eth-account",
        "mnemonic",
        "bip32utils",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.6",
)
