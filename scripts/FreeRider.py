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
    for acc in accounts[1:]:
        acc.transfer(deployer, '990 ether')

    NFT_PRICE = Wei('15 ether')
    AMOUNT_OF_NFTS = 6
    MARKETPLACE_INITIAL_ETH_BALANCE = Wei('90 ether')
    BUYER_PAYOUT = Wei('45 ether')

    UNISWAP_INITIAL_TOKEN_RESERVE = Wei('15000 ether')
    UNISWAP_INITIAL_WETH_RESERVE = Wei('9000 ether')

    with contextlib.redirect_stdout(None):
        attacker = accounts.add()
        buyer = accounts.add()
    deployer.transfer(attacker, '0.5 ether')
    deployer.transfer(buyer, BUYER_PAYOUT)

    # deploy tokens to be traded
    weth = WETH9.deploy({'from': deployer})
    token = DamnValuableToken.deploy({'from': deployer})

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

    pair = interface.IUniswapV2Pair(factory.getPair(token, weth))
    assert pair.token0() == token.address
    assert pair.token1() == weth.address
    assert pair.balanceOf(deployer) > 0

    # deploy the marketplace and get associated ERC721 token
    marketplace = FreeRiderNFTMarketplace.deploy(AMOUNT_OF_NFTS,
                    {'from': deployer, 'value': MARKETPLACE_INITIAL_ETH_BALANCE})

    nft = DamnValuableNFT.at(marketplace.token())

    # ensure deployer owns all minted NFTs
    for i in range(AMOUNT_OF_NFTS):
        assert nft.ownerOf(i) == deployer.address
    nft.setApprovalForAll(marketplace, True, {'from': deployer})

    marketplace.offerMany(
        list(range(AMOUNT_OF_NFTS)),
        [NFT_PRICE] * AMOUNT_OF_NFTS)

    assert marketplace.amountOfOffers() == 6

    buyerContract = FreeRiderBuyer.deploy(attacker, nft,
                                           {'from': buyer, 'value': BUYER_PAYOUT})

    # Exploit code here
    attack = FreeRiderAttack.deploy(
        pair, weth, nft, marketplace, buyerContract, {'from': attacker})
    attack.attack({'from': attacker})

    # Success conditions
    assert attacker.balance() > BUYER_PAYOUT
    assert buyerContract.balance() == 0

    for i in range(AMOUNT_OF_NFTS):
        nft.transferFrom(buyerContract, buyer, i, {'from': buyer})
        assert nft.ownerOf(i) == buyer.address

    assert marketplace.amountOfOffers() == 0
    assert marketplace.balance() < MARKETPLACE_INITIAL_ETH_BALANCE

    print('Challenge successfully passed.')

