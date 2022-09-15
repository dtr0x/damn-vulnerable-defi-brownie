from brownie import *

def main():
    deployer = a[0]
    attacker = a[1]

    ETHER_IN_POOL = Wei('1000 ether')
    ETHER_IN_RECEIVER = Wei('10 ether')

    pool = NaiveReceiverLenderPool.deploy({'from': deployer})
    receiver = FlashLoanReceiver.deploy(pool, {'from': deployer})

    deployer.transfer(pool, ETHER_IN_POOL)
    assert pool.balance() == ETHER_IN_POOL

    assert pool.fixedFee() == Wei('1 ether')

    a[2].transfer(receiver, ETHER_IN_RECEIVER)

    assert receiver.balance() == ETHER_IN_RECEIVER

    # Exploit code here
    attack = NaiveReceiverAttack.deploy({'from': attacker})
    attack.attack(pool, receiver)

    # Success condition - receiver balance is 0
    assert receiver.balance() == 0
    assert pool.balance() == ETHER_IN_POOL + ETHER_IN_RECEIVER

    print('Challenge successfully passed.')

