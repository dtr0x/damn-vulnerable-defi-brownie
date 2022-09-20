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

    return vault
    # Exploit code here
    # Success conditions

    print('Challenge successfully passed.')

