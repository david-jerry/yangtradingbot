import time
import requests
# import cctx

from decimal import Decimal
from typing import Final
from web3 import Web3
from decouple import config
from asgiref.sync import sync_to_async
from logger import LOGGER
from utils_data import load_user_data, update_snipes
from uniswap import Uniswap

from mnemonic import Mnemonic
from eth_account import Account

INFURA_ID: Final = config("INFURA_ID")
MORALIS_API_KEY: Final = config("MORALIS_API_KEY")
ETHERAPI: Final = config('ETHERSCAN')
BINANCEAPI: Final = config('BINANCE_API')
CONTRACTABI: Final = config('CONTRACT_ABI')
UNISWAPABI: Final = config('UNISWAP_ABI')
UNISWAP_ROUTER: Final = config('UNISWAP_ROUTER')
# exchange = cctx.binance({
#     'apiKey': BINANCEAPI,
#     'enableRateLimit': True,
# })
eth: Final = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' #config('WETH', default='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

eth_abi = """[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]"""

async def get_creation_block(token, api=ETHERAPI):
    api_url = "http://api.etherscan.io/api"
    address = token
    api_key = api

    # Define the parameters for the API request
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "apikey": api_key,
    }

    try:
        # Make the API request
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Check if the API response contains a "result" field
            if "result" in data:
                # Access the first transaction in the list (which is the creation transaction)
                creation_transaction = data["result"][0]

                # Extract the blockNumber from the creation transaction
                creation_block_number = creation_transaction["blockNumber"]
                
                print(f"Creation Block Number: {creation_block_number}")
                return creation_block_number
            else:
                print("No result found in API response.")
        else:
            print("API request failed with status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", str(e))

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
    
async def get_token_full_information(token_address, user_data):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    checksum_address = token_address
    if not w3.is_address(checksum_address.strip().lower()):
        return f"An error occurred: Invalid address format", '', '', '', '', '', '', '', '', ''
    
    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address.strip().lower())
                
    abi = await get_contract_abi(checksum_address)

    eth_abi = await get_contract_abi(eth)
    
    token_contract = w3.eth.contract(address=checksum_address, abi=abi)
    eth_contract = w3.eth.contract(address=eth, abi=eth_abi)
                
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
    uniswap3 = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=3, provider=provider)
    uniswap1 = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=1, provider=provider)

    # Get the owner address from the contract
    owner_address = token_contract.functions.owner().call()

    # get block age
    deployment_block_number = await get_creation_block(checksum_address, api=ETHERAPI)

    # Get the current block number
    current_block_number = w3.eth.block_number

    # Calculate the token age in seconds
    blocks_since_deployment = current_block_number - int(deployment_block_number)
    block_info = w3.eth.get_block(current_block_number)
    token_age_seconds = blocks_since_deployment #* block_info['timestamp']
    
    # token_age_seconds=54
    token_decimals = token_contract.functions.decimals().call()
    
    market_price = uniswap.get_price_output(eth, checksum_address, 10**token_decimals)
    LOGGER.info(market_price)
    LOGGER.info(w3.from_wei(market_price, 'ether'))
    current_exchange_rate = uniswap1.get_exchange_rate(checksum_address)
    total_supply = token_contract.functions.totalSupply().call() / 10**token_decimals
    eth_total_supply = eth_contract.functions.totalSupply().call() / 10**18
    crypto_price_usd = 0.0
    token_price = 0.00
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        data = response.json()
        crypto_price_usd = data['ethereum']['usd']
        token_price = (crypto_price_usd) * float(w3.from_wei(market_price, 'ether'))
        LOGGER.info(crypto_price_usd)
    except Exception as e:
        print(f'Error fetching price data: {e}')
        
    busd_price = uniswap.get_price_output(eth, '0x4Fabb145d64652a948d72533023f6E7A623C7C53', 1 * 10**18)
    LOGGER.info(busd_price / 10**18)
    LOGGER.info(total_supply)
    LOGGER.info(token_price)
    LOGGER.info(current_exchange_rate)
    market_cap = token_price * float(total_supply)
    LOGGER.info(current_exchange_rate)
    
# usd * 1eth token of the token
    
    try:
        token_balance = w3.from_wei(uniswap.get_token_balance(checksum_address), 'ether')
        
        eth_balance = uniswap.get_eth_balance()
        token_liquidity_positions = uniswap3.get_liquidity_positions()
        token_metadata = token_contract.functions.name().call()
        token_symbol = token_contract.functions.symbol().call()
        return token_balance, token_symbol, token_decimals, eth_balance / 10**token_decimals, token_price, token_metadata, token_liquidity_positions, owner_address, token_age_seconds, market_cap
    except Exception as e:
        LOGGER.info(e)
        return "Error retrieving token informations.", '', '', '', '', '', '', '', '', ''


    
async def get_token_info(token_address, network, user_data, api_key=ETHERAPI):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
    
    checksum_address = token_address
    if not w3.is_address(checksum_address.strip().lower()):
        return f"An error occurred: Invalid address format", "", "", "", "", ""
    
    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address.strip().lower())
                

    try:
        LOGGER.info("Initializing the Transfer")
        abi = await get_contract_abi(checksum_address)
        token_contract = w3.eth.contract(address=checksum_address, abi=abi)
        LOGGER.info(f'Token Contract: {token_contract}')
        provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
        
        try:
            uni_abi = """[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":true,"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"FeeAmountEnabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":false,"internalType":"int24","name":"tickSpacing","type":"int24"},{"indexed":false,"internalType":"address","name":"pool","type":"address"}],"name":"PoolCreated","type":"event"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"createPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"enableFeeAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"","type":"uint24"}],"name":"feeAmountTickSpacing","outputs":[{"internalType":"int24","name":"","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint24","name":"","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"parameters","outputs":[{"internalType":"address","name":"factory","type":"address"},{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"}],"name":"setOwner","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
            uni_v3_pool = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
            univ3 = w3.eth.contract(uni_v3_pool, abi=uni_abi)
        except Exception as e:
            return "Error getting Uniswap V3 Instance", "", "", "", "", ""
        
        lp = ""
        try:
            lp = univ3.functions.getPool(checksum_address, eth, 10000).call()
            LOGGER.info(lp)
            if lp == "0x0000000000000000000000000000000000000000":
                lp = univ3.functions.createPool(checksum_address, eth, 10000).call()
        except Exception as e:     
            LOGGER.error(f"Error Occured: {e}")       

        # uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=3, provider=provider)
        
        # lp=""
        # try:
        #     # info = uniswap.get_liquidity_positions()
        #     # LOGGER,info(info)
        #     # lp = uniswap.get_pool_instance(checksum_address, eth, 10000)
        #     # LOGGER.info(lp)
        # except Exception as e:
        #     if '0 address returned. Pool does not exist' in str(e):
        #         LOGGER.info("Exception running")
        #         # lp = uniswap.create_pool_instance(checksum_address, eth, 10000)
        #         LOGGER.error(f"Error Occured: {e}")
        #         # LOGGER.info(lp)
        #     else:
        #         LOGGER.error(f"Error Occured: {e}")

        # Get the functions for retrieving the name and symbol
        name_function = token_contract.functions.name()
        symbol_function = token_contract.functions.symbol()
        token_decimals = token_contract.functions.decimals().call()
        token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
        val = w3.from_wei(token_balance_wei, 'ether')
        # Call the functions to retrieve the name and symbol
        token_name = name_function.call()
        token_symbol = symbol_function.call()
        LOGGER.info("Updating the sniper information")
        if user_data.sniper.exists():
            token_info = await update_snipes(user_data.user_id, checksum_address, {'name': token_name, 'symbol': token_symbol, 'decimal': token_decimals})
            LOGGER.info(token_info)
        return token_name, token_symbol, int(token_decimals), lp, val, checksum_address
    except Exception as e:
        LOGGER.info(e)
        return f'An error occurred: {e}', "", "", "", "", ""
    
async def get_token_info_erc20(token_address, network, user_data, api_key=ETHERAPI):
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
    
    checksum_address = token_address
    if not w3.is_address(checksum_address):
        return f"An error occurred: Invalid address format\n\n{e}", '', "", "", '', ''
    
    if not w3.is_checksum_address(token_address):
        checksum_address = w3.to_checksum_address(token_address)

    # # Define the Etherscan API URL
    # etherscan_api_url = 'https://api.etherscan.io/api'

    # # Define the parameters for the API request
    # params = {
    #     'module': 'token',
    #     'action': 'tokeninfo',
    #     'contractaddress': contract_address,
    #     'apikey': api_key,
    # }

    # try:
    #     # Send a GET request to Etherscan API
    #     response = requests.get(etherscan_api_url, params=params)

    #     # Check if the request was successful
    #     if response.status_code == 200:
    #         data = response.json()
    #         if data['status'] == '1':
    #             info = data['result']
    #             token_name = info['tokenName']
    #             token_symbol = info['symbol']
    #             contract_add = info['contractAddress']
    #             total_supply = info['totalSupply']
    #             token_type = info['tokenType']
    #             prince_usd = info['tokenPriceUSD']
    #             description = info['description']
    #             return token_name, token_symbol, contract_add, total_supply, token_type, prince_usd, description
    #         else:
    #             LOGGER.info(data["message"])
    #             return f'Failed to retrieve ABI for contract {contract_address}. Error: {data["message"]}'
    #     else:
    #         LOGGER.info(response.status_code)
    #         return f'Failed to retrieve ABI for contract {contract_address}. HTTP Error: {response.status_code}'
    try:
        LOGGER.info("Initializing the Transfer")
        abi = await get_contract_abi(checksum_address)
        token_contract = w3.eth.contract(address=checksum_address, abi=abi)
        LOGGER.info(f'Token Contract: {token_contract}')
        provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
        
        try:
            uni_abi = """[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":true,"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"FeeAmountEnabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":false,"internalType":"int24","name":"tickSpacing","type":"int24"},{"indexed":false,"internalType":"address","name":"pool","type":"address"}],"name":"PoolCreated","type":"event"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"createPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"enableFeeAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"","type":"uint24"}],"name":"feeAmountTickSpacing","outputs":[{"internalType":"int24","name":"","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint24","name":"","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"parameters","outputs":[{"internalType":"address","name":"factory","type":"address"},{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"}],"name":"setOwner","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
            uni_v3_pool = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
            univ3 = w3.eth.contract(uni_v3_pool, abi=uni_abi)
        except Exception as e:
            return "Error getting Uniswap V3 Instance", "", "", "", "", ""
        
        lp = ""
        try:
            lp = univ3.functions.getPool(checksum_address, eth, 10000).call()
            LOGGER.info(lp)
            if lp == "0x0000000000000000000000000000000000000000":
                lp = univ3.functions.createPool(checksum_address, eth, 10000).call()
        except Exception as e:     
            LOGGER.error(f"Error Occured: {e}")  
                    
        

        # Get the functions for retrieving the name and symbol
        name_function = token_contract.functions.name()
        token_decimals = token_contract.functions.decimals().call()
        symbol_function = token_contract.functions.symbol()
        token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
        val = w3.from_wei(token_balance_wei, 'ether')
        # Call the functions to retrieve the name and symbol
        token_name = name_function.call()
        token_symbol = symbol_function.call()
        return token_name, token_symbol, int(token_decimals), lp, val, checksum_address
    except Exception as e:
        LOGGER.info(e)
        return f'An error occurred: {e}', "", "", "", '', ''



    
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
    gas_price = w3.from_wei(round(price, 8), unit)
    return gas_price

async def get_default_gas_price_gwei():
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    gas_price = w3.eth.gas_price
    gas_price_gwei = w3.from_wei(round(gas_price, 8), 'gwei')
    return gas_price_gwei


async def attach_wallet_function(network, user_id, key):
    user_data = await load_user_data(user_id)
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    if user_data.wallet_address != None:
        if network.upper() == "ETH":
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase
        elif network.upper() == "BSC":
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase
        elif network.upper() == "ARB":
            w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase
        elif network.upper() == "BASE":
            w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
            wallet_address = w3.eth.account.from_key(key)
            mnemonic_phrase = wallet_address._get_mnemonic()
            return mnemonic_phrase
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

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        res = response.json()
        contract_abi = res['result']
        if contract_abi != '':
            return contract_abi
        else:
            return None
    else:
        return 
        
async def get_token_balance(network, token_address, user_data):
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BSC" and user_data.BSC_added:
        w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.bnbchain.org:443"))
    elif network.upper() == "ARB" and user_data.ARB_added:
        w3 = Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_ID}"))
    elif network.upper() == "BASE" and user_data.BASE_added:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org/"))
    
    abi = await get_contract_abi(token_address)
    
    if not w3.is_checksum_address(token_address):
        checksum_address = w3.to_checksum_address(token_address)
    elif w3.is_checksum_address(token_address):
        checksum_address = token_address
        
    token_contract = w3.eth.contract(address=checksum_address, abi=abi)
    LOGGER.info(token_contract)
    try:
        token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
        LOGGER.info(f"TOKEN Bal: {token_balance_wei}")
    except Exception as e:
        return f"Error Trasferring: {e}", 0.00, "ETH", "ETHEREUM"
    
    balance = w3.from_wei(token_balance_wei, 'ether')
    return balance
            
async def trasnfer_currency(network, user_data, percentage, to_address, token_address=None):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    chain_id = w3.eth.chain_id
    nonce = w3.eth.get_transaction_count(user_data.wallet_address)
    
    per = float(percentage.replace(' %', '').replace('%', ''))
    percentage = float(per / 100)
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
    
    fmt_address = to_address
    if not w3.is_address(fmt_address.strip().lower()):
        return f"Error Trasferring: Invalid address format", 0.00, "ETH", "ETHEREUM"
    
    if not w3.is_checksum_address(fmt_address.strip().lower()):
        fmt_address = w3.to_checksum_address(to_address.strip().lower())

    LOGGER.info(fmt_address)
    LOGGER.info(user_data.wallet_address)

    # gas_estimate = w3.eth.estimate_gas({'to': fmt_address, 'from': user_data.wallet_address, 'value': w3.to_int(val)})
    # LOGGER.info(f"GasEstimate: {w3.to_wei(gas_estimate, 'gwei')}")
    # LOGGER.info(f"Gas Price: {w3.to_wei((gas_estimate), 'gwei')}")
    
    
    
    try:
        gas_price = w3.to_wei('20', 'wei')
        
        # contract_abi = await get_contract_abi(str(token_address)) if token_address != None else None
        # Build the transaction
        if token_address == None:
            balance = float(w3.from_wei(w3.eth.get_balance(user_data.wallet_address), 'ether'))
            amount = balance * percentage

            if balance - amount < float(w3.from_wei(gas_price, 'ether')):
                LOGGER.info('We got here: insufficient funds')
                return f"Insufficient balance\n\nBal: {balance - amount}\nGas Required: {float(w3.from_wei(gas_price, 'ether'))}", amount, "ETH", "ETHEREUM"

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
            eth_balance = w3.eth.get_balance(user_data.wallet_address)
            checksum_address = token_address
            if not w3.is_address(checksum_address.strip().lower()):
                return f"Error Trasferring: Invalid address format", 0.00, "ETH", "ETHEREUM"

            if not w3.is_checksum_address(checksum_address.strip().lower()):
                checksum_address = w3.to_checksum_address(token_address)
            
            abi = await get_contract_abi(checksum_address)
            LOGGER.info(abi)
            

            LOGGER.info(checksum_address)
            LOGGER.info(user_data.wallet_address)
            
            # Create a contract instance for the USDT token
            token_contract = w3.eth.contract(address=checksum_address, abi=abi)
            LOGGER.info(token_contract)
            try:
                token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
                LOGGER.info(f"TOKEN Bal Wei: {token_balance_wei}")
            except Exception as e:
                return f"Error Trasferring: {e}", 0.00, "ETH", "ETHEREUM"
            
            val = w3.from_wei(token_balance_wei, 'ether')
            amount = w3.to_wei(float(val) * percentage, 'ether')
            fmt_gas_est = token_contract.functions.transfer(fmt_address, amount).estimate_gas({"from": user_data.wallet_address})
            gas_estimate = fmt_gas_est
            LOGGER.info(f"Token Bal: {val}")
            LOGGER.info(f"Transfer Amount: {w3.from_wei(amount, 'ether')}")
            LOGGER.info(f"Bal Left: {val - w3.from_wei(amount, 'ether')}")
            LOGGER.info(f"ETH Balance: {w3.from_wei(eth_balance, 'ether')}")
            LOGGER.info(f"Gas Fee in ETH: {w3.from_wei(fmt_gas_est, 'ether')}")
            exp_gas = w3.from_wei(gas_estimate, 'ether')
            gas =  exp_gas 
            LOGGER.info(f"Gas Price: {gas}")
            
            
            if eth_balance < fmt_gas_est:
                return f"Insufficient balance\n\nETH Bal: {w3.from_wei(eth_balance, 'ether')}\nGas Required: {w3.from_wei(fmt_gas_est, 'ether')}", w3.from_wei(amount, 'ether'), "ETH", "ETHEREUM"

            try:
                fmt_amount = w3.from_wei(amount, 'ether')
                # Prepare the transaction to transfer USDT tokens
                transaction = token_contract.functions.transfer(fmt_address, amount).build_transaction({
                    'chainId': 1,  # Mainnet
                    'gas': gas_estimate,  # Gas limit (adjust as needed)
                    # 'gasPrice': w3.to_wei('24', 'gwei'),  # Gas price in Gwei (adjust as needed)
                    'maxFeePerGas': w3.to_wei(53, 'gwei'),
                    'maxPriorityFeePerGas': w3.to_wei(50, 'gwei'),
                    'nonce': nonce,
                })

                signed_transaction = w3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                LOGGER.info(tx_hash.hex())
                token_name, token_symbol, token_decimals, token_lp, balance, contract_add= await get_token_info(checksum_address, network, user_data)
                return tx_hash.hex(), fmt_amount, token_symbol, token_name
            except Exception as e:
                return f"Error Transferring: {e}", 0.00, "ETH", "ETHEREUM"
    except Exception as e:
        LOGGER.error(e)
        return f"Error Transferring: {e}", 0.00000000, 'ETH', 'ETHEREUM'
    


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
 
 
 
 
async def snipping_run(user_data, token_address, buy_price_threshold, sell_price_threshold, auto, method, liquidity, buy=False):
    # Implement logic to fetch liquidity data for the symbol
    # You may need to use an API provided by a liquidity tracking service or exchange
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    
    eth_trading_amount = user_data.snipes.first().eth
    yng_trading_amount = user_data.snipes.first().token
    
    checksum_address = token_address
    if not w3.is_address(checksum_address.strip().lower()):
        return f"Error Trasferring: Invalid address format"

    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address)

    eth_checksum_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" or "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
    if not w3.is_address(eth_checksum_address.strip().lower()):
        return f"Error Trasferring: Invalid address format"

    if not w3.is_checksum_address(eth_checksum_address.strip().lower()):
        eth_checksum_address = w3.to_checksum_address(token_address)
            
    abi = await get_contract_abi(checksum_address)
    
    
    # Create a contract instance for the USDT token
    token_contract = w3.eth.contract(address=checksum_address, abi=abi)
    LOGGER.info(token_contract)
    
    
    try:
        token_balance_wei = token_contract.functions.balanceOf(user_data.wallet_address).call()
        LOGGER.info(f"TOKEN Bal Wei: {token_balance_wei}")
    except Exception as e:
        return f"Error getting token balance: {e}"
    token_name, token_symbol, token_decimals, token_lp, balance, contract_add= await get_token_info(checksum_address, "eth", user_data)
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=1, provider=provider)
    
    token_price = uniswap.get_ex_token_balance(checksum_address)

    fee = False

    if auto:
        uniswap.remove_liquidity(checksum_address, 1*10**token_decimals)
        token_price = uniswap.get_ex_token_balance(checksum_address)
    elif method:
        uniswap.remove_liquidity(checksum_address, 1*10**token_decimals)
        token_price = uniswap.get_ex_token_balance(checksum_address)
    elif liquidity:
        uniswap.add_liquidity(checksum_address, 1*10**token_decimals)
        token_price = uniswap.get_ex_token_balance(checksum_address)
        
    
    # if token_price == buy_price_threshold and buy_price_threshold > 0 or buy:
    #     result = buy_token(eth_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
    #     LOGGER.info(result)
    #     return result

    # elif token_price == sell_price_threshold and sell_price_threshold > 0 or not buy:
    #     result = sell_token(yng_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
    #     LOGGER.info(result)
    #     return result
        
    else:
        await snipping_run(user_data, token_address, buy_price_threshold, sell_price_threshold, auto, method, liquidity)



        
    LOGGER.info(f"buy {buy_price_threshold}")
    LOGGER.info(f"sell {sell_price_threshold}")
    LOGGER.info(f"token {token_price}")
    



# 



async def buyTokenWithEth(user_data, amount, token_address, botname="Yang Bot", token_name='Yangbot', request_eth=True, token=False):
    time.sleep(1)
    LOGGER.info("Starting the Buy Swapping")
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
    try:       
        nonce = web3.eth.get_transaction_count(user_data.wallet_address)
        user_address = user_data.wallet_address
        private_key = user_data.wallet_private_key
        gas = web3.eth.gas_price
        gasPrice = int(user_data.max_gas + gas)
        slippage = user_data.slippage
        
        # ----------------------------------------------------------
        # checksum check
        # ----------------------------------------------------------
        
        checksum_address = token_address
        if not web3.is_address(checksum_address.strip().lower()):
            return f"Error Trasferring: Invalid address format"

        if not web3.is_checksum_address(checksum_address.strip().lower()):
            checksum_address = web3.to_checksum_address(token_address)
        # ----------------------------------------------------------
               
        # ----------------------------------------------------------
        # abi and contract setup
        # ----------------------------------------------------------
        
        contract_abi = await get_contract_abi(checksum_address)
        contract = web3.eth.contract(address=checksum_address, abi=contract_abi)
        # ----------------------------------------------------------
        
        
        # ----------------------------------------------------------
        # convert raw token amount to eth
        # ----------------------------------------------------------
        
        if not request_eth and token:
            amount = web3.from_wei(amount, 'ether')
            LOGGER.info(f"TOKEN WEI: {amount}")
            amount = uniswap.get_price_output(eth, checksum_address, int(amount * 10**18))
            tx_amount = web3.from_wei(amount, 'ether')
            LOGGER.info(f'Converted TOKEN - ETH: {tx_amount}')
        else:
            tx_amount = web3.from_wei(amount, 'ether')
            LOGGER.info(f'ETH: {tx_amount}')
            
            
        userBalance = web3.eth.get_balance(user_address)
        tokenBalance = contract.functions.balanceOf(user_address).call()
        
        if userBalance < amount:
            LOGGER.info("Insufficient Balance")
            return f"""
<strong>{botname} Response</strong>        
❌ Insufficient Balance

Your balance is {web3.from_wei(userBalance, 'ether')} ETH and you requested for {tx_amount} ETH        
        """
        else:
            uniswapRouter = UNISWAP_ROUTER
            uniswapRouter = uniswapRouter.lower()
            uniswapRouter = web3.to_checksum_address(uniswapRouter)
            uniswapABI = UNISWAPABI
            uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
            weth = eth.lower()
            weth = web3.to_checksum_address(weth)
            amountOutMin = uniContract.functions.getAmountsOut(amount, [weth, checksum_address]).call()[1]
            LOGGER.info(f"Converted Amount From Uniswap: {amount}")
            tx_token_amount = uniswap.get_price_output(weth, checksum_address, amount)
            LOGGER.info(f"Amount in WEI: {amount}")
            amountOutMin = amount - (amount * slippage/100)
            amountOutMin = int(amountOutMin)
            LOGGER.info(f"Amount After Slippage: {amountOutMin}")           
            
            
            # ------------------------------------------------
            # only needed if swapping for eth
            # ----------------------------------------------------------
            
            # allowance = contract.functions.allowance(user_address, uniswapRouter).call()
            # approve_tx = contract.functions.approve(
            #     uniswapRouter,
            #     amount).build_transaction({
            #     'gas': 10000000,
            #     'gasPrice':web3.eth.gas_price,
            #     'nonce': web3.eth.get_transaction_count(user_address),
            #     'from': user_address,
            #     })
            # signed_txn = web3.eth.account.sign_transaction(approve_tx, private_key)
            # tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            # LOGGER.info(f"Approval TXHASH: {tx_token.hex()}")
            # allowance = contract.functions.allowance(user_address, uniswapRouter).call()
            # LOGGER.info(f"Allowance Amount: {allowance}")                                                     
            # web3.eth.wait_for_transaction_receipt(tx_token)
            # ------------------------------------------------

            LOGGER.info(f"Amount Before Transaction: {web3.from_wei(amount, 'ether')}")
            estimated_gas = uniContract.functions.swapExactETHForTokens(
                amountOutMin,
                [weth, checksum_address],
                user_address,
                int(time.time()) + 10000,
            ).estimate_gas({"from": user_address, 'value':amount})
            LOGGER.info(f"Estimated Gas Fee: {web3.from_wei(estimated_gas, 'wei')}\nGas Price: {web3.from_wei(gasPrice, 'wei')}\nGas: {gas}")
            
            
            # swapExactETHForTokensSupportingFeeOnTransferTokens
            uniswap_txn = uniContract.functions.swapExactETHForTokens(
                amountOutMin,
                [weth, checksum_address],
                user_address,
                int(time.time()) + 10000,
                ).build_transaction({
                    'from': user_address,
                    'value': amount,
                    'gas':estimated_gas,
                    'maxFeePerGas': web3.to_wei(25, 'gwei'),
                    'maxPriorityFeePerGas': web3.to_wei(20, 'gwei'),
                    'nonce': web3.eth.get_transaction_count(user_address),
                })
            signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
            tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            LOGGER.info(f"Swapped Completed: {tx_token.hex()}")
            web3.eth.wait_for_transaction_receipt(tx_token)
            
            # transfer fee
            # ----------------------------------------------------------------
            # initializing the fee transaction
            tx_fee = web3.to_wei(float(web3.from_wei(amount, 'ether')) * 0.004, 'ether')
            # gas_est = contract.functions.transfer('0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22', tx_fee).estimate_gas({"from": user_data.wallet_address})
            # transaction = contract.functions.transfer('0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22', tx_fee).build_transaction({
            #     'chainId': 1,  # Mainnet
            #     'gas': gas_est,  # Gas limit (adjust as needed)
            #     # 'gasPrice': w3.to_wei('24', 'gwei'),  # Gas price in Gwei (adjust as needed)
            #     'maxFeePerGas': web3.to_wei(53, 'gwei'),
            #     'maxPriorityFeePerGas': web3.to_wei(50, 'gwei'),
            #     'nonce': web3.eth.get_transaction_count(user_data.wallet_address),
            # })

            # signed_transaction = web3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
            tx_hash = await fee_transfer(web3, tx_fee, user_address, private_key)
            # ----------------------------------------------------------------
            
            
            new_userBalance = contract.functions.balanceOf(user_address).call()
            amount = new_userBalance - tokenBalance
            amount = web3.from_wei(amount, 'ether')
            LOGGER.info(amount)
            tx_hash = tx_token.hex()
            LOGGER.info(f"https://etherscan.io/tx/{tx_hash}")
            return f"""
<strong>{botname} Response</strong>        
Purchase of <pre>{tx_amount} ETH</pre> for <pre>{tx_token_amount} {token_name}</pre>  
Transaction Fee: <pre>{web3.from_wei(tx_fee, 'ether')} ETH</pre>
-------------------------------------------
Transaction Hash: <pre>https://etherscan.io/tx/{tx_hash}</pre>   
        """
    except Exception as e:
        print(e)
        return f"""
<strong>{botname} Response</strong>        
❌ There was an error.

Error Details: <pre>{e}</pre>    
    """


async def sellTokenForEth(user_data, amount, token_address, botname="Yang Bot", token_name='Yangbot', request_eth=False):
    time.sleep(1)
    LOGGER.info("Starting the Sell Swapping")
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
    try:
        user_address = user_data.wallet_address
        private_key = user_data.wallet_private_key
        slippage = user_data.slippage
        
        checksum_address = token_address
        if not web3.is_address(checksum_address.strip().lower()):
            return f"Error Trasferring: Invalid address format"

        if not web3.is_checksum_address(checksum_address.strip().lower()):
            checksum_address = web3.to_checksum_address(token_address)
            
        # token address contract and abi 
        contract_abi = await get_contract_abi(checksum_address)
        contract = web3.eth.contract(address=checksum_address, abi=contract_abi)

                    
        if not request_eth:
            tx_token_amount = web3.from_wei(amount, 'ether')
            tx_amount = uniswap.get_price_output(eth, checksum_address, amount)
            LOGGER.info(f"Token Amount: {tx_token_amount}\nUniswap Amount ETH: {web3.from_wei(tx_amount, 'ether')}")
        else:
            LOGGER.info(amount)
            tx_amount = amount
            converted_token_amount = uniswap.get_price_output(checksum_address, eth, amount)
            LOGGER.info(converted_token_amount)
            tx_token_amount = web3.from_wei(converted_token_amount, 'ether')
            amount = converted_token_amount
            LOGGER.info(f"ETH - Token: {web3.from_wei(tx_amount, 'ether')}\nToken: {tx_token_amount}")
            amount = web3.to_wei(tx_token_amount, 'ether')
        ethBalance = web3.eth.get_balance(user_address)
        userBalance = contract.functions.balanceOf(user_address).call()

        perc = tx_amount * 0.004
        
        if ethBalance <= (0 + perc) or ethBalance < (300000 + perc):
            LOGGER.info("Insufficient Balance")
            return f"""
<strong>{botname} Response</strong>        
❌ Insufficient Gas Fee to complete the transaction

Your token balance is {web3.from_wei(userBalance, 'ether')} {token_name} and you requested for {web3.from_wei(tx_amount, 'ether')} ETH worth of {tx_token_amount} {token_name}       
"""
        else:
            uniswapRouter = UNISWAP_ROUTER
            uniswapRouter = uniswapRouter.lower()
            uniswapRouter = web3.to_checksum_address(uniswapRouter)
            LOGGER.info(uniswapRouter)
            uniswapABI = UNISWAPABI
            uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
            weth = web3.to_checksum_address(eth.lower())
            # amountOutMin = uniContract.functions.getAmountsIn(amount, [weth, checksum_address]).call()[0]
            # LOGGER.info(amountOutMin)
            # # amountOutMin = amountOutMin - (amountOutMin * slippage/100) if slippage > 0.000000000000 else amountOutMin
            # amountOutMin = int(amountOutMin)
            # LOGGER.info(amountOutMin)
            amountInMin = uniContract.functions.getAmountsOut(amount, [checksum_address, weth]).call()[1]
            amountInEth = float(web3.from_wei(amountInMin, 'ether'))
            amountInMin = web3.to_wei(amountInEth - ((amountInEth * float(slippage))/100), 'ether')
            amountOutMin = amountInMin
            LOGGER.info(f"Amount Out: {amountOutMin}")
            
            tx_fee = web3.to_wei((float(web3.from_wei(tx_amount, 'ether')) * 0.004), 'ether')

            # allowance approval
            allowance = contract.functions.allowance(user_address, uniswapRouter).call()
            LOGGER.info(f"Allowance: {allowance}")
            
            if allowance < amount:
                maxApprove = 2**256 - 1
                gas_est = contract.functions.approve(uniswapRouter, maxApprove).estimate_gas({"from": user_data.wallet_address})
                
                approve_tx = contract.functions.approve(
                    uniswapRouter,
                    maxApprove).build_transaction({
                    'gas': gas_est,
                    # 'gasPrice': gas_est,
                    'maxFeePerGas': web3.to_wei(33, 'gwei'),
                    'maxPriorityFeePerGas': web3.to_wei(20, 'gwei'),
                    'nonce': web3.eth.get_transaction_count(user_address),
                    'from': user_address,
                    })
                signed_txn = web3.eth.account.sign_transaction(approve_tx, private_key)
                approve_tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                LOGGER.info(f"Approval TXHASH: {approve_tx_token.hex()}")
                await web3.eth.wait_for_transaction_receipt(approve_tx_token)
                LOGGER.info("Approved Transaction")
            else:
                LOGGER.info("Already approved")
            # ------------------------------------------------------------------
            
            print("Hello print statement::: ", amount, amountOutMin, [checksum_address, weth], user_address)
            
            gas_est = uniContract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount,
                amountOutMin,
                [checksum_address, weth],
                user_address,
                int(time.time()) + 10000,
            ).estimate_gas({"from": user_address})
            LOGGER.info(f"Gas Extimate For uniswap tranxaction: {gas_est}")
            uniswap_txn = uniContract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount,
                amountOutMin,
                [checksum_address, weth],
                user_address,
                int(time.time()) + 100000,
                ).build_transaction({
                    'gas': 300000,
                    'from': user_address,
                    # 'gasPrice': gas_est,
                    'maxFeePerGas': web3.to_wei(23, 'gwei'),
                    'maxPriorityFeePerGas': web3.to_wei(20, 'gwei'),
                    'nonce': web3.eth.get_transaction_count(user_address),
                })
            signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
            tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            LOGGER.info("Signed Transaction")
            web3.eth.wait_for_transaction_receipt(tx_token)
            LOGGER.info("Swap Completed")
            
            
            # transfer fee
            # -------------------------------------
            # gas_est = contract.functions.transfer('0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22', tx_fee).estimate_gas({"from": user_data.wallet_address})
            LOGGER.info("Initiating fee transfer")
            # contract = web3.eth.contract(address=eth, abi=eth_abi)
            # gas_est = contract.functions.transfer('0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22', tx_fee).estimate_gas()
            # transaction = contract.functions.transfer('0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22', tx_fee).build_transaction({
            #     'chainId': 1,  # Mainnet
            #     'gas': 30000,  # Gas limit (adjust as needed)
            #     'gasPrice': gas_est,
            #     # 'maxFeePerGas': web3.to_wei(53, 'gwei'),
            #     # 'maxPriorityFeePerGas': web3.to_wei(50, 'gwei'),
            #     'nonce': web3.eth.get_transaction_count(user_data.wallet_address),
            # })

            # signed_transaction = web3.eth.account.sign_transaction(transaction, user_data.wallet_private_key)
            # fee_tx_token = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            # LOGGER.info("Fee has be paid")
            # web3.eth.wait_for_transaction_receipt(fee_tx_token)
            fee_tx_hash = await fee_transfer(web3, tx_fee, user_address, private_key)
            # -------------------------------------
            
            
            new_userBalance = web3.eth.get_balance(user_address)
            amount = new_userBalance - ethBalance
            LOGGER.info(f"New Bal: {web3.from_wei(new_userBalance, 'ether')}, Eth Bal: {web3.from_wei(ethBalance, 'ether')}")
            amount = web3.from_wei(amount, 'ether')
            LOGGER.info(amount)
            LOGGER.info(tx_token.hex())
            tx_hash = tx_token.hex()
            return f"""
<strong>{botname} Response</strong>        
Sale of <pre>{tx_token_amount} {token_name}</pre> for <pre>{tx_amount} ETH</pre>  
Transaction Fee Taken: {web3.from_wei(tx_fee, 'ether')} <pre>https://etherscan.io/tx/{fee_tx_hash}</pre> 
Transaction Hash: <pre>https://etherscan.io/tx/{tx_hash}</pre>   
        """
    except Exception as e:
        print(e)
        return f"""
<strong>{botname} Response</strong>        
❌ There was an error.

Error Details: <pre>{e}</pre>    
    """
    
async def fee_transfer(w3, amount_wei, user_address, private_key, recipient='0xA1ed97eAbF43bBc82E342E4E016ecCfcc085dA22'):
    # gas_est = w3.eth.estimate_gas({'to': recipient, 'value': amount_wei})
    # transaction = {
    #     'chainId': 1,  # Mainnet
    #     'to': recipient,
    #     'value': amount_wei,
    #     'gas': 2000000,
    #     'gasPrice': web3.to_wei('50', 'gwei'),
    #     'nonce': w3.eth.get_transaction_count(user_address),
    # }
    # signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    # # Send the transaction
    # transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # # Wait for the transaction to be mined
    # w3.eth.wait_for_transaction_receipt(transaction_hash)
    # return transaction_hash.hex()
    pass
    
async def approve_token(token_address, user_data, balance, decimals):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    
    checksum_address = token_address
    if not w3.is_address(checksum_address.strip().lower()):
        return f"Error Trasferring: Invalid address format"

    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address)
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
    try:
        result = uniswap.approve(checksum_address, balance * 10**decimals)
        LOGGER.info(result)
        return result
    except Exception as e:
        LOGGER.info(e)
        return f"❌ {e}"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# async def processs_buy_or_sell_only(eth_amount, user_data, token_address, decimals,  token_name='Yangbot', balance=0.00, buy=True):
#     w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
#     provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    
#     checksum_address = token_address
#     if not w3.is_address(checksum_address.strip().lower()):
#         return f"Error Trasferring: Invalid address format"

#     if not w3.is_checksum_address(checksum_address.strip().lower()):
#         checksum_address = w3.to_checksum_address(token_address)

#     eth_checksum_address = eth
        
#     uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
#     try:
#         if buy:
#             eth_in_wei = eth_amount * 10**decimals
#             LOGGER.info(f"FMT Amount: {int(eth_in_wei)}")
#             token_in_eth = uniswap.get_price_input(eth, checksum_address, int(eth_in_wei))
#             LOGGER.info(f"Token Amount: {token_in_eth}")
#             LOGGER.info(buy)
#             buy_result = buy_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
#             LOGGER.info(buy_result)
#             return f"""
# Approving your purchase of: {eth_in_wei / 10**decimals} {token_name}
            
# {buy_result}
#             """
#         elif not buy:
#             eth_in_wei = (eth_amount * float(balance)) * 10**decimals
#             LOGGER.info(f"FMT Amount: {w3.from_wei(eth_in_wei, 'ether')} {token_name}")
#             eth_to_get_from_token = uniswap.get_price_output(checksum_address, eth, int(eth_in_wei))
#             LOGGER.info(f"ETH To Get: {eth_to_get_from_token / 10**decimals}")
#             LOGGER.info(buy)
#             sell_result = sell_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
#             LOGGER.info(sell_result)
#             return f"""
# Approving your sale of: {eth_in_wei / 10**decimals} {token_name}
            
# {sell_result}
#             """
#         elif buy == "buymaxtoken":
#             eth_in_wei = (eth_amount * float(balance)) * 10**decimals
#             LOGGER.info(f"FMT Amount: {w3.from_wei(eth_in_wei, 'ether')} {token_name}")
#             eth_to_get_from_token = uniswap.get_price_input(eth, checksum_address, int(eth_in_wei))
#             LOGGER.info(f"ETH To Get: {eth_to_get_from_token / 10**decimals}")
#             LOGGER.info(buy)
#             buy_result = buy_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
#             LOGGER.info(buy_result)
#             return f"""
# Approving your purchase of: {eth_in_wei / 10**decimals} {token_name}
            
# {sell_result}
#             """
#         elif buy == "sellmaxtoken":
#             eth_in_wei = (eth_amount * float(balance)) * 10**decimals
#             LOGGER.info(f"FMT Amount: {w3.from_wei(eth_in_wei, 'ether')} {token_name}")
#             eth_to_get_from_token = uniswap.get_price_output(checksum_address, eth, int(eth_in_wei))
#             LOGGER.info(f"ETH To Get: {eth_to_get_from_token / 10**decimals}")
#             LOGGER.info(buy)
#             sell_result = sell_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
#             LOGGER.info(sell_result)
#             return f"""
# Approving your purchase of: {eth_in_wei / 10**decimals} {token_name}
            
# {sell_result}
#             """
#     except Exception as e:
#         return f"❌ {e}"
        
        

# def buy_token(amount, uniswap, token_contract, sending_to, eth=eth):
#     # Returns the amount of DAI you get for 1 ETH (10^18 wei)
#     swap_result = uniswap.make_trade_output(token_contract, eth, amount, sending_to)
#     LOGGER.info(swap_result)
#     return swap_result
    
    
# def sell_token(amount, uniswap, token_contract, sending_to, eth=eth):
#     # Returns the amount of ETH you need to pay (in wei) to get 1000 DAI
#     swap_result = uniswap.make_trade(token_contract, eth, amount, sending_to)
#     LOGGER.info(swap_result)
#     return swap_result
