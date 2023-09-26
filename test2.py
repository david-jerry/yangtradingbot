from worker import worker
from decouple import config
from web3 import Web3
import time
import json
MORALIS_API_KEY = config("MORALIS_API_KEY")
INFURA_ID = config("INFURA_ID")
UNISWAP_ABI = config("UNISWAP_ABI")
INFURA_URL = config("INFURA_URL")
WETH = config("WETH")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

contract_abi = config("CONTRACT_ABI")
def main():
    contract_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [
                {
                    "name": "",
                    "type": "string",
                },
            ],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [
                {
                    "name": "",
                    "type": "string",
                },
            ],
            "type": "function",
        },
    ]
    # user_address = "0xfa7a0232958938202039f4e35216cea65971f876"
    user_address = web3.to_checksum_address(
        '0xfa7a0232958938202039f4e35216cea65971f876')
    gas = web3.eth.gas_price
    print(gas)
    gas = web3.from_wei(gas, 'gwei')
    print(gas)
    slipage = 0.8
    gasLimit = 300000
    gasPrice = web3.to_wei(1+gas, 'gwei')
    tokenToBuy = web3.to_checksum_address(
        '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984')
    uniswapRouter = web3.to_checksum_address(
        '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
    uniswapABI = UNISWAP_ABI
    contractbuy = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
    weth = web3.to_checksum_address(WETH)
    amountToBuy = web3.to_wei(0.000001, 'ether')
    amountOutMin = contractbuy.functions.getAmountsOut(
        amountToBuy, [weth, tokenToBuy]).call()[1]
    minTokens = amountOutMin - (amountOutMin * slipage)
    minTokens = int(minTokens)
    print(minTokens)
    uniswap_txn = contractbuy.functions.swapExactETHForTokens(
        minTokens,
        [weth, tokenToBuy],
        user_address,
        int(time.time()) + 10000,
    ).build_transaction({
        'from': user_address,
        'value': amountToBuy,
        'gas': gasLimit,
        'gasPrice': gasPrice,
        'nonce': web3.eth.get_transaction_count(user_address),
    })
    signed_txn = web3.eth.account.sign_transaction(
        uniswap_txn, "9fe1a1c3deaeff95847281a1f89b7978cf8a8632f2a6d7d6f215cc92744e9fb4")
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(tx_token.hex())
    tx = web3.eth.wait_for_transaction_receipt(tx_token)
    # print(tx)
    # contract = web3.eth.contract(address=tokenToBuy, abi=contract_abi)
    # name = contract.functions.name().call()
    # symbol = contract.functions.symbol().call()
    # blocknumber = web3.eth.get_block_number()
    # # sell token
    # amountToSell = web3.to_wei(0.001, 'ether')
    # amountOutMin = contractbuy.functions.getAmountsOut(
    #     amountToSell, [weth, tokenToBuy]).call()[1]
    # minEth = amountOutMin - (amountOutMin * slipage)
    # minEth = int(minEth)
    # print(minEth)
    # uniswap_txn = contractbuy.functions.swapExactTokensForETH(
    #     amountToSell,
    #     minEth,
    #     [tokenToBuy, weth],
    #     user_address,
    #     int(time.time()) + 10000,
    # ).build_transaction({
    #     'from': user_address,
    #     'gas': gasLimit,
    #     'gasPrice': gasPrice,
    #     'nonce': web3.eth.get_transaction_count(user_address),
    # })
    # signed_txn = web3.eth.account.sign_transaction(
    #     uniswap_txn, "40f9b44f77cb7fdd6759584285a3f84d5d49b9937c21f79824dde02c49b476bc")
    # tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # print(tx_token.hex())


if(__name__ == '__main__'):
    main()