import pytest 
from brownie import network, Lottery
from scripts.helper_functions import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, fund_contract
import time 
from scripts.deploy_lottery import deploy 

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    account = get_account()
    lottery = deploy()
    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    fund_contract(lottery)
    fund_contract.endLottery({'from': account})
    time.sleep(60)

    assert lottery.recentWinner() == account 
    assert lottery.balance() == 0