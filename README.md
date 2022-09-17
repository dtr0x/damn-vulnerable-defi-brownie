# damn-vulnerable-defi-brownie
Solutions to [Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz) challenges using the [Brownie](https://eth-brownie.readthedocs.io/en/stable/) framework.

## Setup
```
brownie pm install OpenZeppelin/openzeppelin-contracts@4.2.0
brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@4.2.0
brownie pm install safe-global/safe-contracts@1.3.0
```

## Usage
The original setup/deployment scripts for each challenge (found [here](https://github.com/tinchoabbate/damn-vulnerable-defi/tree/master/test)) have been ported to Python in order to be used with the Brownie command line interface. See the [scripts](scripts) folder to find the script for each challenge. To run the solution for a particular challenge, run the following command from the top-level directory:
```
brownie run <ChallengeName>
```
where `<ChallengeName>` is any of
```
Unstoppable, NaiveReceiver, Truster, SideEntrance, TheRewarder, Selfie, Compromised
```


