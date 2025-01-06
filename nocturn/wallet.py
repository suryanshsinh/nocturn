import os
from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from bip32utils import BIP32Key

RPC_ENDPOINTS = {
    "ETH": "https://rpc.ankr.com/eth",
    "POL": "https://rpc.ankr.com/polygon",
    "BSC": "https://bsc-dataseed.binance.org/",
}

class InvalidMnemonicPhrase(Exception):
    pass

class InvalidPrivateKey(Exception):
    pass

class MismatchException(Exception):
    pass

class Wallet:
    def __init__(self, mnemonic_phrase=None, private_key=None):
        self.mnemonic = None
        self.private_key = None
        self.address = None
        self.multichain = None
        
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

    @staticmethod
    def check_balance(address, chain):
        if chain not in RPC_ENDPOINTS:
            raise ValueError(f"Chain {chain} not supported.")
        web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINTS[chain]))
        balance = web3.eth.get_balance(address)
        return web3.from_wei(balance, "ether")
