from decimal import Decimal
from typing import Final
import requests
from web3 import Web3
from decouple import config
from asgiref.sync import sync_to_async

from logger import LOGGER
from utils_data import load_user_data

INFURA_ID: Final = config("INFURA_ID")
MORALIS_API_KEY: Final = config("MORALIS_API_KEY")
ETHERAPI: Final = config('ETHERSCAN')

def currency_amount(symbol):
    # API endpoint
    url = "https://api.coingecko.com/api/v3/simple/price"

    # Query parameters
    params = {"ids": symbol, "vs_currencies": "usd"}

    # Send GET request to the API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(data)
        price = data[symbol]["usd"]
        LOGGER.info(price)
        return Decimal(price)
    else:
        LOGGER.info(response.json())
        return False


from mnemonic import Mnemonic
from eth_account import Account

def back_variable(message, context, text, markup, caption, markup_reply):
    if "message_stack" not in context.user_data:
        context.user_data["message_stack"] = []
    
    context.user_data["message_stack"].append(
        {"message": message, "text": text, "markup": markup, "caption": caption, "markup_reply": markup_reply}
    )
    
async def get_default_gas_price():
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    gas_price = w3.eth.gas_price
    return gas_price

async def get_default_gas_price_gwei():
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    gas_price = w3.eth.gas_price
    gas_price_gwei = w3.from_wei(gas_price, 'gwei')
    return gas_price_gwei


async def attach_wallet_function(network, user_id, key):
    user_data = await load_user_data(user_id)
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    if user_data:
        if network.upper() == "ETH" and user_data.wallet_address:
            balance = w3.eth.get_balance(user_data.wallet_address)
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            LOGGER.info(mnemonic_phrase)
            return (mnemonic_phrase, wallet_address)
        elif network.upper() == "BSC" and user_data.BSC_added:
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return (mnemonic_phrase, wallet_address)
        elif network.upper() == "ARB" and user_data.ARB_added:
            w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return (mnemonic_phrase, wallet_address)
        elif network.upper() == "BASE" and user_data.BASE_added:
            w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
            balance = w3.eth.get_balance(user_data.wallet_address)    
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return (mnemonic_phrase, wallet_address)
    else:
        return None


async def get_wallet_balance(network, user_id):
    user_data = await load_user_data(user_id)
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    if user_data:
        if network.upper() == "ETH" and user_data.wallet_address:
            balance = w3.eth.get_balance(user_data.wallet_address)
            return balance
        elif network.upper() == "BSC" and user_data.BSC_added:
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            return balance
        elif network.upper() == "ARB" and user_data.ARB_added:
            w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            return balance
        elif network.upper() == "BASE" and user_data.BASE_added:
            w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
            balance = w3.eth.get_balance(user_data.wallet_address)            
            return balance
    else:
        return None

async def generate_wallet(network, user_id):
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=256)
    mnemonic_phrase = words
    LOGGER.info(mnemonic_phrase)
    
    user_data = await load_user_data(user_id)
    

    # Connect to Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Generate BSC wallet
    w3.eth.account.enable_unaudited_hdwallet_features()
    w3_account = w3.eth.account.from_mnemonic(str(mnemonic_phrase))
    ethereum_private_key = w3_account._private_key.hex()

    if network.upper() == "ETH":
        balance = w3.eth.get_balance(w3_account.address)

        return (
            user_data.wallet_address if user_data.wallet_address != None else w3_account.address,
            user_data.wallet_private_key if user_data.wallet_private_key != None else w3_account._private_key.hex(),
            balance,
            user_data.wallet_phrase if user_data.wallet_phrase != None else mnemonic_phrase,
        )
    elif network.upper() == "BSC":
        # Connect to BSC node
        LOGGER.info("Creating BSC wallet")
        bsc_w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
        bsc_account = bsc_w3.eth.account.from_key(ethereum_private_key)
        # Generate BSC wallet
        balance = bsc_w3.eth.get_balance(bsc_account.address)

        return (
            user_data.wallet_address if user_data.wallet_address != None else bsc_account.address,
            user_data.wallet_private_key if user_data.wallet_private_key != None else w3_account._private_key.hex(),
            balance,
            user_data.wallet_phrase if user_data.wallet_phrase != None else mnemonic_phrase,
        )
    elif network.upper() == "ARB":
        # Connect to Avalanche C-Chain node
        LOGGER.info("Creating ARB wallet")
        w3 = Web3(
            Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}")
        )
        arb_account = w3.eth.account.from_key(ethereum_private_key)
        # Generate ARB wallet
        balance = w3.eth.get_balance(arb_account.address)

        return (
            user_data.wallet_address if user_data.wallet_address != None else arb_account.address,
            user_data.wallet_private_key if user_data.wallet_private_key != None else w3_account._private_key.hex(),
            balance,
            user_data.wallet_phrase if user_data.wallet_phrase != None else mnemonic_phrase,
        )
    elif network.upper() == "BASE":
        # Connect to Basechain node (Replace with the actual Basechain RPC URL)
        LOGGER.info("Creating BASE wallet")
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
        base_account = w3.eth.account.from_key(ethereum_private_key)
        # Generate BASE wallet
        balance = w3.eth.get_balance(base_account.address)

        return (
            user_data.wallet_address if user_data.wallet_address != None else base_account.address,
            user_data.wallet_private_key if user_data.wallet_private_key != None else w3_account._private_key.hex(),
            balance,
            user_data.wallet_phrase if user_data.wallet_phrase != None else mnemonic_phrase,
        )


async def trasnfer_currency(network, user_data, amount_in_usd, to_address, token_address=None):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    chain_id = w3.eth.chain_id
    get_gas_price = get_default_gas_price_gwei()
    nonce = w3.eth.getTransactionCount(user_data.wallet_address)
    if network.upper() == "ETH" and user_data.wallet_address:
        amount = w3.toWei(Decimal(amount_in_usd.replace(' USD', '')), 'ether')
        balance = w3.eth.get_balance(user_data.wallet_address)
        contract_abi = w3.eth.contract(address=token_address).abi if token_address != None else w3.eth.contract(address='0x2170Ed0880ac9A755fd29B2688956BD959F933F8').abi
        if balance < amount:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
        amount = w3.toWei(Decimal(amount_in_usd.replace(' USD', '')), 'ether')
        balance = w3.eth.get_balance(user_data.wallet_address)
        contract_abi = w3.eth.contract(address=token_address).abi if token_address != None else w3.eth.contract(address='0x2170Ed0880ac9A755fd29B2688956BD959F933F8').abi
        if balance < amount:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
        amount = w3.toWei(Decimal(amount_in_usd.replace(' USD', '')), 'ether')
        balance = w3.eth.get_balance(user_data.wallet_address)
        contract_abi = w3.eth.contract(address=token_address).abi if token_address != None else w3.eth.contract(address='0x2170Ed0880ac9A755fd29B2688956BD959F933F8').abi
        if balance < amount:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
        amount = w3.toWei(Decimal(amount_in_usd.replace(' USD', '')), 'ether')
        balance = w3.eth.get_balance(user_data.wallet_address)   
        contract_abi = w3.eth.contract(address=token_address).abi if token_address != None else w3.eth.contract(address='0x2170Ed0880ac9A755fd29B2688956BD959F933F8').abi
        if balance < amount:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id         
    

    # Build the transaction
    contract = w3.eth.contract(address=token_address, abi=contract_abi)
    transaction = {
        'to': token_address,
        'value': 0,
        'gas': 2000000,  # Adjust gas limit as needed
        'gasPrice': get_gas_price,  # Adjust gas price as needed
        'nonce': nonce,
        'data': contract.functions.transfer(to_address, amount).buildTransaction({'chainId': chain_id}),
    }

    signed_transaction = w3.eth.account.signTransaction(transaction, user_data.wallet_private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    return tx_hash


async def check_transaction_status(network, user_data,  tx_hash):
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
    
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt