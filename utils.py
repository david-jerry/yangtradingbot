from decimal import Decimal
from typing import Final
import requests
from web3 import Web3
from decouple import config
from asgiref.sync import sync_to_async

from logger import LOGGER
from utils_data import load_user_data

from mnemonic import Mnemonic
from eth_account import Account

INFURA_ID: Final = config("INFURA_ID")
MORALIS_API_KEY: Final = config("MORALIS_API_KEY")
ETHERAPI: Final = config('ETHERSCAN')

async def get_contract_abi(contract_address, api_key=ETHERAPI):
    # Define the Etherscan API URL
    etherscan_api_url = 'https://api.etherscan.io/api'

    # Define the parameters for the API request
    params = {
        'module': 'contract',
        'action': 'getabi',
        'address': contract_address,
        'apikey': api_key,
    }

    try:
        # Send a GET request to Etherscan API
        response = requests.get(etherscan_api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1':
                abi = data['result']
                return abi
            else:
                return f'Failed to retrieve ABI for contract {contract_address}. Error: {data["message"]}'
        else:
            return f'Failed to retrieve ABI for contract {contract_address}. HTTP Error: {response.status_code}'

    except Exception as e:
        return f'An error occurred: {str(e)}'
    
async def currency_amount(symbol):
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

def back_variable(message, context, text, markup, caption, markup_reply):
    if "message_stack" not in context.user_data:
        context.user_data["message_stack"] = []
    
    context.user_data["message_stack"].append(
        {"message": message, "text": text, "markup": markup, "caption": caption, "markup_reply": markup_reply}
    )
    
async def get_default_gas_price(unit='ether'):
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    price = w3.eth.gas_price
    gas_price = w3.from_wei(price, unit)
    return gas_price

async def get_default_gas_price_gwei():
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    gas_price = w3.eth.gas_price
    gas_price_gwei = w3.from_wei(int(gas_price), 'gwei')
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
            return w3.from_wei(balance, 'ether')
        elif network.upper() == "BSC" and user_data.BSC_added:
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            return w3.from_wei(balance, 'ether')
        elif network.upper() == "ARB" and user_data.ARB_added:
            w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            return w3.from_wei(balance, 'ether')
        elif network.upper() == "BASE" and user_data.BASE_added:
            w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
            balance = w3.eth.get_balance(user_data.wallet_address)            
            return w3.from_wei(balance, 'ether')
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

async def get_contract_abi(contract_address):
    api_url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERAPI}'
    LOGGER.info(api_url)

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        res = response.json()
        LOGGER.info(res)
        contract_abi = res['result']
        if contract_abi != '':
            return contract_abi
        else:
            return None
    else:
        return 
        
        
async def trasnfer_currency(network, user_data, amount_in_usd, to_address, token_address=None):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    chain_id = w3.eth.chain_id
    get_gas_price = await get_default_gas_price_gwei()
    nonce = w3.eth.get_transaction_count(user_data.wallet_address)
    price = await currency_amount('ethereum')
    if network.upper() == "ETH" and user_data.wallet_address:
        LOGGER.info('Checking status here')
        amount = Decimal(amount_in_usd) / Decimal(price)
        balance = w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether')
        if balance < amount and balance < 0.00000000:
            LOGGER.info('We got here: insufficient funds')
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
        amount = Decimal(amount_in_usd) / Decimal(price)
        balance = w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether')
        if balance < amount and balance < 0.00000000:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
        amount = Decimal(amount_in_usd) / Decimal(price)
        balance = w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether')
        if balance < amount and balance < 0.00000000:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
        amount = Decimal(amount_in_usd) / Decimal(price)
        balance = w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether')   
        if balance < amount and balance < 0.00000000:
            return "Insufficient balance"
        chain_id = w3.eth.chain_id         
    

    gas_estimate = w3.eth.estimate_gas({'to': to_address, 'from': user_data.wallet_address, 'value': w3.to_wei(amount, 'wei')})
    LOGGER.info(f"GasEstimate: {w3.to_wei(gas_estimate, 'gwei')}")
    LOGGER.info(f"Gas Price: {w3.to_wei((gas_estimate), 'gwei')}")
    
    
    gas_price = w3.to_wei('20', 'gwei')
    
    value = round(amount, 6)
    
    
    if balance - amount < w3.from_wei(gas_price, 'ether'):
        return "Insufficient balance"
    
    
    # contract_abi = await get_contract_abi(str(token_address)) if token_address != None else None
    # Build the transaction
    if token_address == None:
        transaction = {
            'to': to_address,
            'from': user_data.wallet_address,
            'nonce': nonce,
            'chainId': int(chain_id),
            'value': value,
            'gas': gas_estimate, # if user_data.max_gas < 21 else w3.to_wei(user_data.max_gas, 'wei'),
            'gasPrice': gas_price if user_data.max_gas_price < 14 else w3.to_wei(str(int(user_data.max_gas_price)), 'gwei'),
            # 'maxFeePerGas': w3.to_wei(2, 'gwei'),
            # 'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
            # 'data': contract.functions.transfer(to_address, amount).build_transaction({'chainId': chain_id}),
        }
    else:
        abi = await get_contract_abi(token_address)
        # Create a contract instance for the USDT token
        token_contract = w3.eth.contract(address=token_address, abi=abi)

        # Prepare the transaction to transfer USDT tokens
        transaction = token_contract.functions.transfer(to_address, w3.to_wei(value)).buildTransaction({
            'chainId': 1,  # Mainnet
            'gas': gas_estimate,  # Gas limit (adjust as needed)
            'gasPrice': w3.toWei('20', 'gwei'),  # Gas price in Gwei (adjust as needed)
            'nonce': nonce,
        })


    signed_transaction = w3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    LOGGER.info(tx_hash.hex())
    return tx_hash.hex(), value


async def check_transaction_status(network, user_data,  tx_hash):
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt
    # amount_wei = receipt['logs'][0]['data']

    # # Convert the amount from Wei to Ether
    # amount_ether = w3.from_wei(int(amount_wei, 16), 'ether')
    # return amount_ether