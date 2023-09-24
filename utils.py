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
from utils_data import load_user_data, update_snipes
from uniswap import Uniswap

from mnemonic import Mnemonic
from eth_account import Account
UNISWAP_ABI = config("UNISWAP_ABI")
WETH = config("WETH")
INFURA_URL = config("INFURA_URL")
UNISWAP_ROUTER =config("UNISWAP_ROUTER")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
CONTRACT_ABI = config("CONTRACT_ABI")
INFURA_ID: Final = config("INFURA_ID")
MORALIS_API_KEY: Final = config("MORALIS_API_KEY")
ETHERAPI: Final = config('ETHERAPI')
# BINANCEAPI: Final = config('BINANCE_API')

# exchange = cctx.binance({
#     'apiKey': BINANCEAPI,
#     'enableRateLimit': True,
# })

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
    
async def get_token_info(token_address, network, user_data, api_key=ETHERAPI):
    if network.upper() == "ETH" and user_data.wallet_address:
        w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    price = w3.eth.gas_price
    gas_price = w3.from_wei(price, unit)
    return gas_price

async def get_default_gas_price_gwei():
    # Connect to your Ethereum node
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))

    # Get the current gas price (in wei)
    gas_price = w3.eth.gas_price
    gas_price_gwei = w3.from_wei(int(gas_price), 'gwei')
    return gas_price_gwei


async def attach_wallet_function(network, user_id, key):
    user_data = await load_user_data(user_id)
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))

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
        w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
    w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
        w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_ID}"))
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
        result = buy(eth_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
        LOGGER.info(result)
        return result

    elif token_price == sell_price_threshold and sell_price_threshold > 0 or not buy:
        result = sell(yng_trading_amount, token_decimals, uniswap, checksum_address, user_data.wallet_address)
        LOGGER.info(result)
        return result
        
    else:
        await snipping_run(user_data, token_address, buy_price_threshold, sell_price_threshold, auto, method, liquidity)



        
    LOGGER.info(f"buy {buy_price_threshold}")
    LOGGER.info(f"sell {sell_price_threshold}")
    LOGGER.info(f"token {token_price}")
    


def buy(amount, decimal, uniswap, token_contract, sending_to, eth='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'):
    # Returns the amount of DAI you get for 1 ETH (10^18 wei)
    swap_result = uniswap.make_trade_output(token_contract, eth, amount*10**decimal, sending_to)
    LOGGER.info(swap_result)
    return swap_result
    
    
def sell(amount, decimal, uniswap, token_contract, sending_to, eth='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'):
    # Returns the amount of ETH you need to pay (in wei) to get 1000 DAI
    swap_result = uniswap.make_trade(token_contract, eth, amount*10**decimal, sending_to)
    LOGGER.info(swap_result)
    return swap_result


def buyExactlyEth(user_data,copytrade_data,tokenbuy):
    user_address = user_data['wallet_address']
    private_key = user_data['wallet_private_key']
    gasPrice = user_data['max_gas_price']
    gasLimit = user_data['max_gas']
    slipage = copytrade_data['slipage']
    token_address = tokenbuy
    amount = copytrade_data['amount']
    amount = int(amount)
    amount = Web3.to_wei(amount, 'ether')
    userBalance = web3.eth.get_balance(user_address)
    if userBalance < amount:
        LOGGER.info("Insufficient Balance")
    else:
        uniswapRouter = web3.toChecksumAddress(UNISWAP_ROUTER)
        uniswapABI = UNISWAP_ABI
        uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
        weth = web3.to_checksum_address(WETH)
        amountOutMin = uniContract.functions.getAmountsOut(amount, [weth, token_address]).call()[1]
        amountOutMin = amountOutMin - (amountOutMin * slipage)
        amountOutMin = int(amountOutMin)
        uniswap_txn = uniContract.functions.swapExactETHForTokens(
            amountOutMin,
            [weth, token_address],
            user_address,
            int(time.time()) + 10000,
            ).build_transaction({
                'from': user_address,
                'value': amount,
                'gas': gasLimit,
                'gasPrice': gasPrice,
                'nonce': web3.eth.get_transaction_count(user_address),
            })
        signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(tx_token.hex())


def sellExactlyToken(user_data,copytrade_data,tokensell):
    user_address = user_data['wallet_address']
    private_key = user_data['wallet_private_key']
    gasPrice = user_data['max_gas_price']
    gasLimit = user_data['max_gas']
    slipage = copytrade_data['slipage']
    token_address = tokensell
    amount = copytrade_data['amount']
    amount = int(amount)
    amount = Web3.to_wei(amount, 'ether')
    contract = web3.eth.contract(address=token_address, abi=CONTRACT_ABI)
    userBalance = contract.functions.balanceOf(user_address).call()
    if userBalance <= 0:
        LOGGER.info("Insufficient Balance")

    else:
        uniswapRouter = web3.toChecksumAddress(UNISWAP_ROUTER)
        uniswapABI = UNISWAP_ABI
        uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
        weth = web3.to_checksum_address(WETH)
        amountOutMin = uniContract.functions.getAmountsOut(amount, [token_address, weth]).call()[1]
        amountOutMin = amountOutMin - (amountOutMin * slipage)
        amountOutMin = int(amountOutMin)
        allowance = contract.functions.allowance(user_address, uniswapRouter).call()
        approve_tx = contract.functions.approve(
            uniswapRouter,
            amount).build_transaction({
            'gas': gasLimit,
            'gasPrice':gasPrice,
            'nonce': web3.eth.get_transaction_count(user_address),
            'from': user_address,
            })
        signed_txn = web3.eth.account.sign_transaction(approve_tx, private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(tx_token.hex())
        allowance = contract.functions.allowance(user_address, uniswapRouter).call()
        print(allowance)                                                     
        while contract.functions.allowance(user_address, uniswapRouter).call() != amount:
            print("waiting for approval")
        print("approved")
        allowance = contract.functions.allowance(user_address, uniswapRouter).call()
        print(allowance)
        uniswap_txn = uniContract.functions.swapExactTokensForETH(
            amount,
            amountOutMin,
            [token_address, weth],
            user_address,
            int(time.time()) + 10000,
            ).build_transaction({
                'from': user_address,
                'gas': gasLimit,
                'gasPrice': gasPrice,
                'nonce': web3.eth.get_transaction_count(user_address),
            })
        signed_txn = web3.eth.account.sign_transaction(uniswap_txn, private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(tx_token.hex())


    






