from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from .exceptions import *
import requests

class Nocturn:
    def to_wei(amount):
        return Web3.to_wei(amount, "ether")
    
    def from_wei(amount):
        return Web3.from_wei(amount, "ether")
    
    def to_currency(amount, currency="usd"):
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies={currency}"
        response = requests.get(url).json()
        if "ethereum" not in response or currency not in response["ethereum"]:
            return None
        return amount * response["ethereum"][currency]
    
    def from_currency(amount, currency="usd"):
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies={currency}"
        response = requests.get(url).json()
        if "ethereum" not in response or currency not in response["ethereum"]:
            return None
        return amount / response["ethereum"][currency]
    
    def fetch_balance(address, rpc_endpoint):
        web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
        return web3.eth.get_balance(address)
    
    def get_transaction_history(address, chain, API_KEY, page, testnet=False, offset=0):
        if chain not in ["eth", "bsc", "pol"]:
            raise InvalidChain("Invalid chain.")
        chain_ids = {
            "testnet": {
                "eth": 11155111, "bsc": 97, "pol": 80002
            }, "mainnet": {
                "eth": 1, "bsc": 56, "pol": 137
            }
        }
        chain_id = chain_ids["testnet" if testnet else "mainnet"][chain]
        url = f"https://api.etherscan.io/v2/api?chainid={chain_id}&module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page={page}&offset=10&sort=desc&apikey={API_KEY}"
        response = requests.get(url).json()
        if "result" not in response or not isinstance(response["result"], list):
            print(f"Error fetching {chain} transactions:", response.get("message", "Unknown error"))
            return []
        return response["result"]

    def send_crypto(private_key, to_address, amount, rpc_endpoint, gas_price=None):
        web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
        to_address = web3.to_checksum_address(to_address)
        if not web3.is_address(to_address):
            raise ValueError("Invalid recipient address.")
        sender_address = web3.eth.account.from_key(private_key).address
        nonce = web3.eth.get_transaction_count(sender_address)
        if gas_price is None:
            gas_price = web3.eth.gas_price
        gas_limit = web3.eth.estimate_gas({"to": to_address, "from": sender_address, "value": amount})
        balance = web3.eth.get_balance(sender_address)
        gas_fee_used = gas_limit * gas_price
        total_cost = amount + gas_fee_used
        if balance < total_cost:
            raise ValueError(f"Insufficient balance. Required: {total_cost} Wei, Available: {balance} Wei")
        tx = {
            "to": to_address,
            "value": amount,
            "gas": gas_limit,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": web3.eth.chain_id
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return {
            "tx_hash": tx_hash.hex(),
            "from": sender_address,
            "to": to_address,
            "amount_sent": amount,
            "gas_limit": gas_limit,
            "gas_price": gas_price,
            "gas_fee_used": gas_fee_used,
            "total_cost": total_cost,
            "balance_before_tx": balance,
            "balance_after_tx": balance - total_cost
        }

    def preview_transaction(private_key, to_address, amount, rpc_endpoint, gas_price=None):
        web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
        to_address = web3.to_checksum_address(to_address)
        if not web3.is_address(to_address):
            raise ValueError("Invalid recipient address.")
        sender_address = web3.eth.account.from_key(private_key).address
        nonce = web3.eth.get_transaction_count(sender_address)
        if gas_price is None:
            gas_price = web3.eth.gas_price
        gas_limit = web3.eth.estimate_gas({"to": to_address, "from": sender_address, "value": amount})
        balance = web3.eth.get_balance(sender_address)
        total_cost = amount + (gas_limit * gas_price)
        return {
            "sender": sender_address,
            "recipient": to_address,
            "amount_to_send": amount,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "estimated_gas_fee": gas_limit * gas_price,
            "total_cost": total_cost,
            "balance_available": balance,
            "can_proceed": balance >= total_cost
        }

class Wallet:
    def __init__(self, ETHERSCAN_API_KEY, mnemonic_phrase=None, private_key=None, rpc_endpoints={}):
        self.RPC_ENDPOINTS = {
            "testnet": {
                "eth": "https://ethereum-sepolia-rpc.publicnode.com",
                "bsc": "https://bsc-testnet.publicnode.com",
                "pol": "https://rpc-amoy.polygon.technology",
            }, "mainnet": {
                "eth": "https://eth.meowrpc.com",
                "bsc": "https://bsc.meowrpc.com",
                "pol": "https://1rpc.io/matic",
            }
        }
        self.set_rpc_endpoints(rpc_endpoints)
        self.ETHERSCAN_API_KEY = ETHERSCAN_API_KEY
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
    
    def set_rpc_endpoints(self, endpoints):
        for net, chains in endpoints.items():
            for chain, endpoint in chains.items():
                self.RPC_ENDPOINTS[net][chain] = endpoint
    
    def fetch_balance(self, chain, testnet=False):
        if chain not in ["eth", "bsc", "pol"]:
            raise InvalidChain("Invalid chain.")
        return Nocturn.fetch_balance(self.address, self.RPC_ENDPOINTS["testnet" if testnet else "mainnet"][chain])

    def get_transaction_history(self, chain, page=1, testnet=False, offset=0):
        if chain not in ["eth", "bsc", "pol"]:
            raise InvalidChain("Invalid chain.")
        return Nocturn.get_transaction_history(self.address, chain, self.ETHERSCAN_API_KEY, page, testnet, offset)

    def send_crypto(self, to_address, amount, chain, testnet=False, gas_price=None):
        if chain not in ["eth", "bsc", "pol"]:
            raise InvalidChain("Invalid chain.")
        return Nocturn.send_crypto(self.private_key, to_address, amount, self.RPC_ENDPOINTS["testnet" if testnet else "mainnet"][chain], gas_price)

    def preview_transaction(self, to_address, amount, chain, testnet=False, gas_price=None):
        if chain not in ["eth", "bsc", "pol"]:
            raise InvalidChain("Invalid chain.")
        return Nocturn.preview_transaction(self.private_key, to_address, amount, self.RPC_ENDPOINTS["testnet" if testnet else "mainnet"][chain], gas_price)
