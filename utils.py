import time
import requests
# import cctx

from decimal import Decimal
from typing import Final
import requests
from web3 import Web3
from decouple import config
from asgiref.sync import sync_to_async

from logger import LOGGER
from utils_data import load_user_data, update_snipes, save_txhash_copy_data
from uniswap import Uniswap

from mnemonic import Mnemonic
from eth_account import Account
UNISWAP_ABI = config("UNISWAP_ABI")
WETH = config("WETH")
INFURA_URL = config("INFURA_URL")
UNISWAP_ROUTER =config("UNISWAP_ROUTER")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
# CONTRACT_ABI = config("CONTRACT_ABI")
INFURA_ID: Final = config("INFURA_ID")
MORALIS_API_KEY: Final = config("MORALIS_API_KEY")
ETHERAPI: Final = config('ETHERSCAN')
BINANCEAPI: Final = config('BINANCE_API')
CONTRACTABI: Final = config('CONTRACT_ABI')
UNISWAPABI: Final = config('UNISWAP_ABI')
# exchange = cctx.binance({
#     'apiKey': BINANCEAPI,
#     'enableRateLimit': True,
# })
eth='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'




contract_abi = [{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},{"internalType":"uint256","name":"mintingAllowedAfter_","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegator","type":"address"},{"indexed":True,"internalType":"address","name":"fromDelegate","type":"address"},{"indexed":True,"internalType":"address","name":"toDelegate","type":"address"}],"name":"DelegateChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegate","type":"address"},{"indexed":False,"internalType":"uint256","name":"previousBalance","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"newBalance","type":"uint256"}],"name":"DelegateVotesChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"minter","type":"address"},{"indexed":False,"internalType":"address","name":"newMinter","type":"address"}],"name":"MinterChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"DELEGATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"checkpoints","outputs":[{"internalType":"uint32","name":"fromBlock","type":"uint32"},{"internalType":"uint96","name":"votes","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"}],"name":"delegate","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"delegateBySig","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"delegates","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"getCurrentVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getPriorVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minimumTimeBetweenMints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"mintCap","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"mintingAllowedAfter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"numCheckpoints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"minter_","type":"address"}],"name":"setMinter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"}]
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
        return f"An error occurred: Invalid address format\n\n{e}", "", "", "", "", ""
    
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

    # Get the timestamp of the block in which the token contract was created
    creation_timestamp = w3.eth.get_block('earliest').timestamp

    # Calculate the age of the token in seconds
    current_timestamp = w3.eth.get_block('latest').timestamp
    token_age_seconds = current_timestamp - creation_timestamp
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
        return token_balance, token_symbol, token_decimals, eth_balance, token_price, token_metadata, token_liquidity_positions, owner_address, token_age_seconds, market_cap
    except Exception as e:
        LOGGER.info(e)
        return "Error retrieving token informations.", '', '', '', '', '', '', '', '', ''


    
async def get_token_info(token_address, network, user_data, api_key=ETHERAPI):
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
        return f"An error occurred: Invalid address format\n\n{e}", "", "", "", "", ""
    
    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address.strip().lower())
        

    try:
        abi = await get_contract_abi(checksum_address)
        LOGGER.info(abi)
        token_contract = w3.eth.contract(address=checksum_address, abi=abi)
        
        provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
        
        uni_abi = """[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":true,"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"FeeAmountEnabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":true,"internalType":"uint24","name":"fee","type":"uint24"},{"indexed":false,"internalType":"int24","name":"tickSpacing","type":"int24"},{"indexed":false,"internalType":"address","name":"pool","type":"address"}],"name":"PoolCreated","type":"event"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"createPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"name":"enableFeeAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint24","name":"","type":"uint24"}],"name":"feeAmountTickSpacing","outputs":[{"internalType":"int24","name":"","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint24","name":"","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"parameters","outputs":[{"internalType":"address","name":"factory","type":"address"},{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickSpacing","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"}],"name":"setOwner","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
        uni_v3_pool = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
        univ3 = w3.eth.contract(uni_v3_pool, abi=uni_abi)
        
        eth='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
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
        token_info = await update_snipes(user_data.user_id, checksum_address, {'name': token_name, 'symbol': token_symbol, 'decimal': token_decimals})
        LOGGER.info(token_info)
        return token_name, token_symbol, int(token_decimals), lp, val, checksum_address
    except Exception as e:
        LOGGER.info(e)
        return f'An error occurred: {e}', "", "", "", "", ""
    
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
        
    
    if token_price == buy_price_threshold and buy_price_threshold > 0 or buy:
        result = buy_token(eth_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
        LOGGER.info(result)
        return result

    elif token_price == sell_price_threshold and sell_price_threshold > 0 or not buy:
        result = sell_token(yng_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
        LOGGER.info(result)
        return result
        
    else:
        await snipping_run(user_data, token_address, buy_price_threshold, sell_price_threshold, auto, method, liquidity)



        
    LOGGER.info(f"buy {buy_price_threshold}")
    LOGGER.info(f"sell {sell_price_threshold}")
    LOGGER.info(f"token {token_price}")
    



async def processs_buy_or_sell_only(eth_amount, user_data, token_address, decimals,  token_name='Yangbot', balance=0.00, buy=True):
    w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_ID}"))
    provider = f"https://mainnet.infura.io/v3/{INFURA_ID}"
    
    checksum_address = token_address
    if not w3.is_address(checksum_address.strip().lower()):
        return f"Error Trasferring: Invalid address format"

    if not w3.is_checksum_address(checksum_address.strip().lower()):
        checksum_address = w3.to_checksum_address(token_address)

    eth_checksum_address = "0x0000000000000000000000000000000000000000"
    if not w3.is_address(eth_checksum_address.strip().lower()):
        return f"Error Trasferring: Invalid address format"

    if not w3.is_checksum_address(eth_checksum_address.strip().lower()):
        eth_checksum_address = w3.to_checksum_address(token_address)
        
    uniswap = Uniswap(address=user_data.wallet_address, private_key=user_data.wallet_private_key, version=2, provider=provider)
    try:
        if buy:
            eth_in_wei = eth_amount * 10**decimals
            LOGGER.info(f"FMT Amount: {int(eth_in_wei)}")
            token_in_eth = uniswap.get_price_input(eth, checksum_address, int(eth_in_wei))
            LOGGER.info(f"Token Amount: {token_in_eth}")
            LOGGER.info(buy)
            buy_result = buy_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
            LOGGER.info(buy_result)
            return f"""
Approving your purchase of: {eth_in_wei / 10**decimals} {token_name}
            
{buy_result}
            """
        elif not buy:
            eth_in_wei = (eth_amount * float(balance)) * 10**decimals
            LOGGER.info(f"FMT Amount: {w3.from_wei(eth_in_wei, 'ether')} {token_name}")
            eth_to_get_from_token = uniswap.get_price_output(checksum_address, eth, int(eth_in_wei))
            LOGGER.info(f"ETH To Get: {eth_to_get_from_token / 10**decimals}")
            LOGGER.info(buy)
            sell_result = sell_token(eth_in_wei, uniswap, checksum_address, user_data.wallet_address, eth=eth)
            LOGGER.info(sell_result)
            return f"""
Approving your sale of: {eth_in_wei / 10**decimals} {token_name}
            
{sell_result}
            """
    except Exception as e:
        return f"{e}"
        
        

def buy_token(amount, uniswap, token_contract, sending_to, eth='0x0000000000000000000000000000000000000000'):
    # Returns the amount of DAI you get for 1 ETH (10^18 wei)
    swap_result = uniswap.make_trade_output(token_contract, eth, amount, sending_to)
    LOGGER.info(swap_result)
    return swap_result
    
    
def sell_token(amount, uniswap, token_contract, sending_to, eth='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'):
    # Returns the amount of ETH you need to pay (in wei) to get 1000 DAI
    swap_result = uniswap.make_trade(token_contract, eth, amount, sending_to)
    LOGGER.info(swap_result)
    return swap_result


def buyExactEth(user_data,copytrade_data,tokenbuy):
    try:
        user_address = user_data['wallet_address']
        private_key = user_data['wallet_private_key']
        gas = web3.eth.gas_price
        gasPrice = copytrade_data['gas_delta']+gas
        gasPrice = web3.to_wei(gasPrice,'gwei')
        slippage = copytrade_data['slippage']
        token_address = tokenbuy.lower()
        token_address = web3.to_checksum_address(token_address)
        contract = web3.eth.contract(address=token_address, abi=contract_abi)
        amount = copytrade_data['amount']
        amount = web3.to_wei(amount, 'ether')
        userBalance = web3.eth.get_balance(user_address)
        tokenBalance = contract.functions.balanceOf(user_address).call()
        if userBalance < amount:
            LOGGER.info("Insufficient Balance")
            return "Insufficient Balance"
        else:
            uniswapRouter = UNISWAP_ROUTER
            uniswapRouter = uniswapRouter.lower()
            uniswapRouter = web3.to_checksum_address(uniswapRouter)
            uniswapABI = UNISWAP_ABI
            uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
            weth = WETH.lower()
            weth = web3.to_checksum_address(weth)
            amountOutMin = uniContract.functions.getAmountsOut(amount, [weth, token_address]).call()[1]
            amountOutMin = amountOutMin - (amountOutMin * slippage/100)
            amountOutMin = int(amountOutMin)
            uniswap_txn = uniContract.functions.swapExactETHForTokens(
                amountOutMin,
                [weth, token_address],
                user_address,
                int(time.time()) + 100000,
                ).build_transaction({
                    'from': user_address,
                    'gas': 300000,
                    'value': amount,
                    'gasPrice': int(gasPrice),
                    'nonce': web3.eth.get_transaction_count(user_address),
                })
            signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
            tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            web3.eth.wait_for_transaction_receipt(tx_token)
            new_userBalance = contract.functions.balanceOf(user_address).call()
            amount = new_userBalance - tokenBalance
            amount = web3.from_wei(amount, 'ether')
            data = {
                'user_id':user_data['user_id'],
                'txhash':tx_token.hex(),
                'amount':amount,
                'token_address':token_address,
                'bot_name':copytrade_data['name'],
            }
            print('data',data)
            save_txhash_copy_data(data)
            return tx_token.hex()
    except Exception as e:
        print(e)
        return None


def sellExactToken(user_data,copytrade_data,tokensell):
        time.sleep(15)
        user_address = user_data['wallet_address']
        private_key = user_data['wallet_private_key']
        gas = web3.eth.gas_price
        gasPrice = copytrade_data['gas_delta']+gas
        gasPrice=web3.to_wei(gasPrice,'gwei')
        slippage = copytrade_data['slippage']
        token_address = tokensell.lower()
        token_address = web3.to_checksum_address(token_address)
        contract = web3.eth.contract(address=token_address, abi=contract_abi)
        amount = contract.functions.balanceOf(user_address).call()
        ethBalance = web3.eth.get_balance(user_address)
        userBalance = contract.functions.balanceOf(user_address).call()
        if userBalance <= 0:
            LOGGER.info("Insufficient Balance")
        else:
            uniswapRouter = UNISWAP_ROUTER
            uniswapRouter = uniswapRouter.lower()
            uniswapRouter = web3.to_checksum_address(uniswapRouter)
            uniswapABI = UNISWAP_ABI
            uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
            weth = web3.to_checksum_address(WETH.lower())
            amountOutMin = uniContract.functions.getAmountsOut(amount, [token_address, weth]).call()[1]
            amountOutMin = amountOutMin - (amountOutMin * slippage/100)
            amountOutMin = int(amountOutMin)
            allowance = contract.functions.allowance(user_address, uniswapRouter).call()
            if allowance < amount:
                maxApprove = 2**256 - 1
                approve_tx = contract.functions.approve(
                    uniswapRouter,
                    maxApprove).build_transaction({  
                    'gasPrice':int(gasPrice),
                    'gas': 300000,
                    'nonce': web3.eth.get_transaction_count(user_address),
                    'from': user_address,
                    })
                signed_txn = web3.eth.account.sign_transaction(approve_tx, private_key)
                tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                print(tx_token.hex())                             
                web3.eth.wait_for_transaction_receipt(tx_token)
                print("aproved---------------------------------")
            else:
                print("already aproved---------------------------------")
                time.sleep(30)    
            uniswap_txn = uniContract.functions.swapExactTokensForETH(
                amount,
                amountOutMin,
                [token_address, weth],
                user_address,
                int(time.time()) + 100000,
                ).build_transaction({
                    'gas': 300000,
                    'from': user_address,
                    'gasPrice': int(gasPrice),
                    'nonce': web3.eth.get_transaction_count(user_address),
                })
            signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
            tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            web3.eth.wait_for_transaction_receipt(tx_token)
            new_userBalance = web3.eth.get_balance(user_address)
            print('new_userBalance',new_userBalance)
            print('ethBalance',ethBalance)
            amounteth = new_userBalance - ethBalance
            print('amounteth',amounteth)
            if amounteth < 0:
                amounteth = 0
            amounteth = web3.from_wei(amounteth, 'ether')
            print('amounteth',amounteth)

            data = {
                'user_id':user_data['user_id'],
                'txhash':tx_token.hex(),
                'amount':amounteth,
                'token_address':weth,
                'bot_name':copytrade_data['name'],
            }
            print('data',data)
            save_txhash_copy_data(data)
            print(tx_token.hex())
            return tx_token.hex()
    


    








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
        return f"{e}"