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
    
async def get_token_info(contract_address, api_key=ETHERAPI):
    # Define the Etherscan API URL
    etherscan_api_url = 'https://api.etherscan.io/api'

    # Define the parameters for the API request
    params = {
        'module': 'token',
        'action': 'getTokenInfo',
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
                info = data['result']
                token_name = info['tokenName']
                token_symbol = info['symbol']
                return token_name, token_symbol
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
            return mnemonic_phrase, wallet_address
        elif network.upper() == "BSC" and user_data.BSC_added:
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase, wallet_address
        elif network.upper() == "ARB" and user_data.ARB_added:
            w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
            balance = w3.eth.get_balance(user_data.wallet_address)
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase, wallet_address
        elif network.upper() == "BASE" and user_data.BASE_added:
            w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
            balance = w3.eth.get_balance(user_data.wallet_address)    
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase, wallet_address
    else:
        return None, None


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
        
        
async def trasnfer_currency(network, user_data, percentage, to_address, token_address=None):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    chain_id = w3.eth.chain_id
    nonce = w3.eth.get_transaction_count(user_data.wallet_address)
    
    per = float(percentage.replace(' %', '').replace('%', ''))
    if network.upper() == "ETH" and user_data.wallet_address:
        LOGGER.info('Checking status here')
        chain_id = w3.eth.chain_id
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
        chain_id = w3.eth.chain_id
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
        chain_id = w3.eth.chain_id
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
        chain_id = w3.eth.chain_id         
    
    if not w3.is_address(to_address):
        return f"Error Trasferring: Invalid address format", 0.00, "ETH", "ETHEREUM"
    elif not w3.is_checksum_address(to_address):
        return f"Error Trasferring: Invalid checksum address format", 0.00, "ETH", "ETHEREUM"
    elif w3.is_address(to_address):
        fmt_address = to_address
    elif w3.is_checksum_address(to_address):
        fmt_address = w3.to_checksum_address(to_address)

    LOGGER.info(fmt_address)
    LOGGER.info(user_data.wallet_address)

    # gas_estimate = w3.eth.estimate_gas({'to': fmt_address, 'from': user_data.wallet_address, 'value': w3.to_int(val)})
    # LOGGER.info(f"GasEstimate: {w3.to_wei(gas_estimate, 'gwei')}")
    # LOGGER.info(f"Gas Price: {w3.to_wei((gas_estimate), 'gwei')}")
    
    
    gas_price = w3.to_wei('20', 'gwei')
    
    try:
        
        # contract_abi = await get_contract_abi(str(token_address)) if token_address != None else None
        # Build the transaction
        if token_address == None:
            balance = float(w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether'))
            amount = balance * per/100

            if balance - amount < w3.from_wei(gas_price, 'ether'):
                LOGGER.info('We got here: insufficient funds')
                return "Insufficient balance", amount, "ETH", "ETHEREUM"

            transaction = {
                'to': fmt_address,
                'from': user_data.wallet_address,
                'nonce': nonce,
                'chainId': int(chain_id),
                'value': w3.to_wei(amount, 'ether'),
                'gas': 21000, # if user_data.max_gas < 21 else w3.to_wei(user_data.max_gas, 'wei'),
                # 'gasPrice': gas_price if user_data.max_gas_price < 14 else w3.to_wei(str(int(user_data.max_gas_price)), 'gwei'),
                'maxFeePerGas': w3.to_wei(25, 'gwei'),
                'maxPriorityFeePerGas': w3.to_wei(20, 'gwei'),
                # 'data': contract.functions.transfer(to_address, amount).build_transaction({'chainId': chain_id}),
            }
            
            signed_transaction = w3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            LOGGER.info(tx_hash.hex())
            return tx_hash.hex(), amount, "ETH", "ETHEREUM"
        else:
            
            abi = await get_contract_abi(token_address)
            LOGGER.info(abi)
            
            checksum_address = w3.to_checksum_address(token_address)
            
            try:
                # Create a contract instance for the USDT token
                token_contract = w3.eth.contract(address=checksum_address, abi=abi)
                token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
                val = w3.to_wei(w3.from_wei(token_balance_wei, 'ether'), 'ether')
                amount = w3.to_wei(val * (per / 100), 'ether')
                gas_estimate = w3.to_wei(token_contract.functions.transfer(fmt_address, amount).estimate_gas({"from": user_data.wallet_address}), 'ether')
                LOGGER.info(f"Token Bal: {val}")
                LOGGER.info(f"Transfer Amount: {amount}")
                LOGGER.info(f"Bal Left{val - amount}")
                LOGGER.info(f"Gas Price: {gas_estimate}")
                
                
                if val - amount < gas_estimate:
                    return "Insufficient balance", amount, "ETH", "ETHEREUM"

                # Prepare the transaction to transfer USDT tokens
                transaction = token_contract.functions.transfer(fmt_address, amount).build_transaction({
                    'chainId': 1,  # Mainnet
                    'gas': gas_price,  # Gas limit (adjust as needed)
                    # 'gasPrice': w3.to_wei('24', 'gwei'),  # Gas price in Gwei (adjust as needed)
                    'maxFeePerGas': w3.to_wei(26, 'gwei'),
                    'maxPriorityFeePerGas': w3.to_wei(24, 'gwei'),
                    'nonce': nonce,
                })

                signed_transaction = w3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                LOGGER.info(tx_hash.hex())
                symbol, symbol_name = await get_token_info(token_address)
                return tx_hash.hex(), amount, symbol, symbol_name
            except Exception as e:
                return e, 0.00, "ETH", "ETHEREUM"
    except Exception as e:
        LOGGER.error(2)
        if token_address == None:
            return f"Error Trasferring: {e}", 0.00000000, "ETH", "ETHEREUM"
        else:
            symbol, symbol_name = await get_token_info(token_address)
            return f"Error Trasferring: {e}", 0.00000000, symbol, symbol_name

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