from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import requests

class Nocturn:
    def to_wei(amount):
        return Web3.to_wei(amount, "ether")
    
    def from_wei(amount):
        return Web3.from_wei(amount, "ether")
    
    def get_prices(API_KEY, chains, currency="usd"):
        CHAIN_SYMBOLS = {
            'eth': 'ETH', 'bsc': 'BNB', 'pol': 'MATIC'
        }
        if not chains:
            raise ValueError("No chain specified.")
        for chain in chains:
            if chain not in CHAIN_SYMBOLS:
                raise InvalidChain("Invalid chain.")
        symbols = ",".join([CHAIN_SYMBOLS[chain] for chain in chains])
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": API_KEY}
        params = {"symbol": symbols, "convert": currency.upper()}
        response = requests.get(url, headers=headers, params=params).json()
        try:
            prices = {
                chain: response["data"][CHAIN_SYMBOLS[chain]][0]["quote"][currency.upper()]["price"]
                for chain in chains
            }
            return prices
        except KeyError:
            raise Exception(f"Price data unavailable for {chain} in {currency}")
    
    def to_currency(API_KEY, amount, chain, currency="usd"):
        price = Nocturn.get_price(API_KEY, [chain], currency)
        return amount * price
    
    def from_currency(API_KEY, amount, chain, currency="usd"):
        price = Nocturn.get_price(API_KEY, [chain], currency)
        return amount / price
    
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
            raise Exception(f"Error fetching {chain} transactions:", response.get("message", "Unknown error"))
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
        estimated_gas_fee = gas_limit * gas_price
        amount_sending = amount - estimated_gas_fee
        if balance < amount:
            raise ValueError(f"Insufficient balance. Required: {amount} Wei, Available: {balance} Wei")
        tx = {
            "to": to_address,
            "value": amount_sending,
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
            "amount_to_send": amount,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "estimated_gas_fee": estimated_gas_fee,
            "amount_sending": amount_sending,
            "balance_available": balance,
            "can_proceed": balance >= amount
        }


    def preview_transaction(private_key, to_address, amount, rpc_endpoint, gas_price=None):
        web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
        to_address = web3.to_checksum_address(to_address)
        if not web3.is_address(to_address):
            raise ValueError("Invalid recipient address.")
        sender_address = web3.eth.account.from_key(private_key).address
        if gas_price is None:
            gas_price = web3.eth.gas_price
        try:
            gas_limit = web3.eth.estimate_gas({"to": to_address, "from": sender_address, "value": amount})
        except:
            return {
                "can_proceed": False,
                "error": "Failed to estimate gas limit."
            }
        balance = web3.eth.get_balance(sender_address)
        estimated_gas_fee = gas_limit * gas_price
        amount_sending = amount - estimated_gas_fee
        return {
            "sender": sender_address,
            "recipient": to_address,
            "amount_to_send": amount,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "estimated_gas_fee": estimated_gas_fee,
            "amount_sending": amount_sending,
            "balance_available": balance,
            "can_proceed": balance >= amount
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
    
    def _generate_mnemonic(self, words=12):
        return Mnemonic("english").generate(strength=128 if words == 12 else 256)
    
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

class InvalidMnemonicPhrase(Exception):
    pass

class MismatchException(Exception):
    pass

class InvalidChain(Exception):
    pass