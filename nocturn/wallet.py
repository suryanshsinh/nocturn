from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from exceptions import *

class Wallet:
    RPC_ENDPOINTS = {
        "testnet": {
            "ETH": "https://rpc.sepolia.org",
            "POL": "https://rpc-mumbai.maticvigil.com",
            "BSC": "https://data-seed-prebsc-1-s1.binance.org:8545/",
        }, 
        "mainnet": {
            "ETH": "https://rpc.ankr.com/eth",
            "POL": "https://rpc.ankr.com/polygon",
            "BSC": "https://bsc-dataseed.binance.org/",
        }
    }

    def __init__(self, mnemonic_phrase=None, private_key=None):
        self.mnemonic = None
        self.private_key = None
        self.address = None
        self.multichain = None
        self.check_balance = self._instance_check_balance
        
        if mnemonic_phrase and private_key:
            raise MismatchException("Both mnemonic and private key cannot be passed at the same time.")
        if mnemonic_phrase:
            if not Mnemonic("english").check(mnemonic_phrase):
                raise InvalidMnemonicPhrase("Invalid mnemonic phrase.")
            self.multichain = True
            self.mnemonic = mnemonic_phrase
            self.private_key = self._mnemonic_to_private_key(mnemonic_phrase)
            self.address = self._private_key_to_address(self.private_key)
        elif private_key:
            self.multichain = False
            self.private_key = private_key
            self.address = self._private_key_to_address(private_key)
        else:
            self.multichain = True
            self.mnemonic = self._generate_mnemonic()
            self.private_key = self._mnemonic_to_private_key(self.mnemonic)
            self.address = self._private_key_to_address(self.private_key)

    def _generate_mnemonic(self):
        return Mnemonic("english").generate(strength=256)

    def _mnemonic_to_private_key(self, mnemonic):
        return BIP32Key.fromEntropy(Mnemonic("english").to_seed(mnemonic)).ChildKey(0).ChildKey(0).PrivateKey().hex()

    def _private_key_to_address(self, private_key):
        return Account.from_key(private_key).address

    def _instance_check_balance(self, chain, testnet=False):
        return Wallet.check_balance(self.address, chain)

    @staticmethod
    def check_balance(address, chain, testnet=False):
        if chain not in Wallet.RPC_ENDPOINTS["testnet" if testnet else "mainnet"]:
            raise ValueError(f"Chain {chain} not supported.")
        web3 = Web3(Web3.HTTPProvider(Wallet.RPC_ENDPOINTS["testnet" if testnet else "mainnet"][chain]))
        balance = web3.eth.get_balance(address)
        return web3.from_wei(balance, "ether")
