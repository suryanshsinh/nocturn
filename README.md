# Nocturn Crypto Wallet

## Introduction

Nocturn is a lightweight Python-based cryptocurrency wallet supporting **Ethereum (ETH), Binance Smart Chain (BSC), and Polygon (POL)**. It enables users to **manage their wallets, check balances, send transactions, and retrieve transaction history** using public blockchain RPC nodes.

The wallet supports both **mainnet** and **testnet** environments and can be accessed using either a **mnemonic phrase** or a **private key**.

---

## Features

- **Multi-chain Support**: Works with **Ethereum, Binance Smart Chain, and Polygon**.
- **Wallet Management**: Generate wallets from a **mnemonic phrase** or **private key**.
- **Transaction Management**:
  - Check account balance.
  - Fetch **transaction history**.
  - Send crypto to any address.
  - Preview transactions before sending.
- **Custom RPC Support**: Use default or custom **RPC endpoints**.
- **Conversion Utilities**: Convert between **ETH, Wei, USD, and other fiat currencies**.

---

# Wallet Class

The `Wallet` class is the primary interface for managing a wallet. It supports **mnemonic phrase-based wallets** and **private key-based wallets**.

### **Initialization**
```python
wallet = Wallet(ETHERSCAN_API_KEY="your_api_key", mnemonic_phrase="your mnemonic phrase")
```
or
```python
wallet = Wallet(ETHERSCAN_API_KEY="your_api_key", private_key="your private key")
```

### **Constructor Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `ETHERSCAN_API_KEY` | `str` | API key for fetching transaction history. |
| `mnemonic_phrase` | `str` (optional) | Mnemonic phrase to generate a wallet. |
| `private_key` | `str` (optional) | Private key to restore an existing wallet. |
| `rpc_endpoints` | `dict` (optional) | Custom RPC endpoints for different chains. |

### **Available Methods**

#### **1. `fetch_balance(chain, testnet=False)`**
Fetches the balance of the wallet in **Wei**.

```python
balance = wallet.fetch_balance("eth")
print(balance)  # Returns balance in Wei
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `chain` | `str` | Blockchain to fetch balance from (`eth`, `bsc`, `pol`). |
| `testnet` | `bool` (optional) | Fetch from testnet if `True`, default is `False`. |

Returns: **`int`** (balance in Wei).

---

#### **2. `get_transaction_history(chain, page=1, testnet=False, offset=0)`**
Fetches transaction history from **Etherscan-compatible APIs**.

```python
transactions = wallet.get_transaction_history("eth", page=1)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `chain` | `str` | Blockchain (`eth`, `bsc`, `pol`). |
| `page` | `int` (optional) | Page number for pagination. Default is `1`. |
| `testnet` | `bool` (optional) | Fetch from testnet if `True`. |
| `offset` | `int` (optional) | Number of transactions to skip. Default is `0`. |

Returns: **`list`** of transaction objects.

---

#### **3. `send_crypto(to_address, amount, chain, testnet=False, gas_price=None)`**
Sends cryptocurrency to a recipient.

```python
tx = wallet.send_crypto("0xRecipientAddress", Web3.to_wei(0.01, "ether"), "eth")
print(tx)  # Returns transaction details
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `to_address` | `str` | Recipient’s wallet address. |
| `amount` | `int` | Amount to send (in Wei). |
| `chain` | `str` | Blockchain (`eth`, `bsc`, `pol`). |
| `testnet` | `bool` (optional) | Send on testnet if `True`. |
| `gas_price` | `int` (optional) | Custom gas price in Wei. If `None`, fetches from the network. |

Returns: **`dict`** containing transaction details including:
- Transaction hash (`tx_hash`)
- Sender and recipient addresses
- Gas limit, gas price, and total gas fee
- Amount sent and remaining balance

---

#### **4. `preview_transaction(to_address, amount, chain, testnet=False, gas_price=None)`**
Simulates a transaction before sending.

```python
preview = wallet.preview_transaction("0xRecipientAddress", Web3.to_wei(0.01, "ether"), "eth")
print(preview)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `to_address` | `str` | Recipient’s wallet address. |
| `amount` | `int` | Amount to send (in Wei). |
| `chain` | `str` | Blockchain (`eth`, `bsc`, `pol`). |
| `testnet` | `bool` (optional) | Send on testnet if `True`. |
| `gas_price` | `int` (optional) | Custom gas price in Wei. |

Returns: **`dict`** with transaction details including:
- Estimated gas fee
- Total cost (amount + gas fee)
- Whether the wallet has enough balance (`can_proceed`)

---

# Nocturn Class

The `Nocturn` class provides **utility functions** for working with crypto assets.

### **1. `to_wei(amount)`**
Converts ETH to Wei.

```python
wei_value = Nocturn.to_wei(0.01)  
```

Returns: **`int`** (Wei equivalent).

---

### **2. `from_wei(amount)`**
Converts Wei to ETH.

```python
eth_value = Nocturn.from_wei(10000000000000000)  
```

Returns: **`float`** (ETH equivalent).

---

### **3. `to_currency(amount, currency="usd")`**
Converts ETH to another currency using **Coingecko API**.

```python
usd_value = Nocturn.to_currency(1, "usd")  
```

Returns: **`float`** (value in the requested currency).

---

### **4. `from_currency(amount, currency="usd")`**
Converts a currency (e.g., USD) to ETH.

```python
eth_amount = Nocturn.from_currency(2000, "usd")  
```

Returns: **`float`** (ETH equivalent).

---

### **5. `fetch_balance(address, rpc_endpoint)`**
Fetches balance for a given wallet address.

```python
balance = Nocturn.fetch_balance("0xYourWalletAddress", "https://eth.meowrpc.com")
```

Returns: **`int`** (balance in Wei).

---

### **6. `get_transaction_history(address, chain, API_KEY, page, testnet=False, offset=0)`**
Fetches transaction history for any address.

```python
transactions = Nocturn.get_transaction_history("0xYourWalletAddress", "eth", "your_api_key", 1)
```

Returns: **`list`** of transaction objects.

---

### **7. `send_crypto(private_key, to_address, amount, rpc_endpoint, gas_price=None)`**
Sends cryptocurrency from a **private key**.

```python
tx = Nocturn.send_crypto("your-private-key", "0xRecipientAddress", Web3.to_wei(0.01, "ether"), "https://eth.meowrpc.com")
```

Returns: **`dict`** containing transaction details.

---

## Conclusion

Nocturn is a powerful, lightweight crypto wallet for managing **ETH, BSC, and POL** transactions. It provides robust tools for sending, receiving, and monitoring transactions while ensuring flexibility with **custom RPC nodes and conversion utilities**.