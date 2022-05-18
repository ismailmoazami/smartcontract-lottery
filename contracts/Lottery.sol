// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase{

    address payable[] public players;
    AggregatorV3Interface internal ethUsdPriceFeed;
    
    enum LOTTEY_STATE{
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    
    uint256 public fee;
    LOTTEY_STATE public lottery_state;
    uint public usdEntryFee;
    bytes32 public keyHash;
    address payable public recentWinner;
    uint256 randomness;
    event RequestedRandomness(bytes32 requestId);

    constructor(address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyHash)
                public VRFConsumerBase(_vrfCoordinator, _link){

        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntryFee = 50 * (10 **18);
        lottery_state = LOTTEY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;

    }

    function enter() public payable{
    
        require(lottery_state == LOTTEY_STATE.OPEN, "Lottery did not open!");
        require(msg.value >= getEntranceFee(), "Not Enough Ethers!");
        players.push(msg.sender);

    }

    function getEntranceFee()public view returns(uint){
        (, int price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint adjustedPrice = (uint(price)) * 10 **10; // 18 decimals

        uint costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;

    }

    function startLottery() public onlyOwner{
        require(lottery_state == LOTTEY_STATE.CLOSED, "Can not start new lottery!");
        lottery_state = LOTTEY_STATE.OPEN;
    }

    function endLottery() public onlyOwner{

        lottery_state = LOTTEY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override{
        require(lottery_state == LOTTEY_STATE.CALCULATING_WINNER, "You're not on the way!");
        require(_randomness>0, "random not found!");

        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);

        players = new address payable[](0);
        randomness = _randomness;

    }   
}