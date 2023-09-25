from worker import worker
from decouple import config
from web3 import Web3
import time
import json
MORALIS_API_KEY= config("MORALIS_API_KEY")
INFURA_ID = config("INFURA_ID")
UNISWAP_ABI = config("UNISWAP_ABI")
INFURA_URL = config("INFURA_URL")
WETH = config("WETH")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract_abi = [{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},{"internalType":"uint256","name":"mintingAllowedAfter_","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegator","type":"address"},{"indexed":True,"internalType":"address","name":"fromDelegate","type":"address"},{"indexed":True,"internalType":"address","name":"toDelegate","type":"address"}],"name":"DelegateChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegate","type":"address"},{"indexed":False,"internalType":"uint256","name":"previousBalance","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"newBalance","type":"uint256"}],"name":"DelegateVotesChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"minter","type":"address"},{"indexed":False,"internalType":"address","name":"newMinter","type":"address"}],"name":"MinterChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"DELEGATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"checkpoints","outputs":[{"internalType":"uint32","name":"fromBlock","type":"uint32"},{"internalType":"uint96","name":"votes","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"}],"name":"delegate","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"delegateBySig","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"delegates","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"getCurrentVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getPriorVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minimumTimeBetweenMints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"mintCap","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"mintingAllowedAfter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"numCheckpoints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"minter_","type":"address"}],"name":"setMinter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"}]
def main():

    # buy token
    path = []
    user_address = web3.to_checksum_address('0xfa7a0232958938202039f4e35216cea65971f876')
    slipage = 0.9
    gasLimit = 10000000
    gasPrice = web3.to_wei(5, 'gwei')
    tokenAddress = web3.to_checksum_address('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984')
    uniswapRouter = web3.to_checksum_address('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
    uniswapABI = UNISWAP_ABI
    uniContract = web3.eth.contract(address=uniswapRouter, abi=uniswapABI)
    weth = web3.to_checksum_address(WETH)
    amountToBuy = web3.to_wei(0.01, 'ether')
    userBalance = web3.eth.get_balance(user_address)
    if userBalance > amountToBuy:
        amountOutMin = uniContract.functions.getAmountsOut(amountToBuy, [weth, tokenAddress]).call()[1]
        minTokens = amountOutMin - (amountOutMin * slipage)
        minTokens = int(minTokens)
        uniswap_txn = uniContract.functions.swapExactETHForTokens(
            minTokens,
            [weth, tokenAddress],
            user_address,
            int(time.time()) + 10000,
            ).build_transaction({
                'from': user_address,
                'value': amountToBuy,
                'gas': gasLimit,
                'gasPrice': gasPrice,
                'nonce': web3.eth.get_transaction_count(user_address),
            })
        signed_txn = web3.eth.account.sign_transaction(uniswap_txn, "9fe1a1c3deaeff95847281a1f89b7978cf8a8632f2a6d7d6f215cc92744e9fb4")
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx = web3.eth.wait_for_transaction_receipt(tx_token)
        print(tx_token.hex())
    
    contract = web3.eth.contract(address=tokenAddress, abi=contract_abi)
    symbol = contract.functions.symbol().call()
    print(symbol)
    userBalance = contract.functions.balanceOf(user_address).call()
    contractsell = web3.eth.contract(address=tokenAddress, abi=contract_abi)
    allowance = contractsell.functions.allowance(user_address, uniswapRouter).call()
    print(allowance)
    amountToBuy = contract.functions.balanceOf(user_address).call()
    approve_tx = contractsell.functions.approve(
        uniswapRouter,
        amountToBuy).build_transaction({
        'gas': gasLimit,
        'gasPrice':gasPrice,
        'nonce': web3.eth.get_transaction_count(user_address),
        'from': user_address,
        })
    signed_txn = web3.eth.account.sign_transaction(approve_tx, "9fe1a1c3deaeff95847281a1f89b7978cf8a8632f2a6d7d6f215cc92744e9fb4")
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print('approve: ', tx_token.hex())
    tx = web3.eth.wait_for_transaction_receipt(tx_token)
    print("approve success")
    allowance = contractsell.functions.allowance(user_address, uniswapRouter).call()
    print(allowance)                                                        

    print('sell')    
    amountOutMin = uniContract.functions.getAmountsOut(userBalance, [tokenAddress,weth]).call()[1]
    minEth = amountOutMin - (amountOutMin * slipage)
    minEth = int(minEth)
    zero = web3.to_wei(0, 'ether')
    uniswap_txn = uniContract.functions.swapExactTokensForETH(
        userBalance,
        minEth,
        [tokenAddress, weth],
        user_address,
        int(time.time()) + 10000,
        ).build_transaction({
            'from': user_address,
            'value': zero,
            'gas': gasLimit,
            'gasPrice': gasPrice,
            'nonce': web3.eth.get_transaction_count(user_address),
        })
    signed_txn = web3.eth.account.sign_transaction(uniswap_txn, "9fe1a1c3deaeff95847281a1f89b7978cf8a8632f2a6d7d6f215cc92744e9fb4")
    tx_token =  web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(tx_token.hex())

if(__name__ == '__main__'):
    main()