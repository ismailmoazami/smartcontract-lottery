
from brownie import accounts, Lottery, network, config, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy 
from scripts.helper_functions import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, get_account, fund_contract
import pytest
import time  

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy()
    
    expected = Web3.toWei(0.025, 'ether')
    entrance_fee = lottery.getEntranceFee()

    assert entrance_fee == expected

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery = deploy()
    
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({'from': get_account(), 'value': lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery = deploy()
    account = get_account()
    lottery.startLottery({'from': account})


    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    
    assert lottery.players(0) == account 

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    account = get_account()
    lottery = deploy()

    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    fund_contract(lottery)
    lottery.endLottery({'from': account})

    
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    account = get_account()
    lottery = deploy()

    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=1), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=2), 'value': lottery.getEntranceFee()})
    
    fund_contract(lottery)
    balance_of_account = get_account(index=0).balance()
    balance_of_contract = lottery.balance()

    transaction = lottery.endLottery({'from': account})
    request_id = transaction.events['RequestedRandomness']['requestId']

    random_number = 777
    get_contract('vrf_coordinator').callBackWithRandomness(request_id, random_number, lottery.address)
    expected = 0
    balance_of_account = get_account(index=0).balance()
    balance_of_contract = lottery.balance()

    assert get_account(index=expected).address == lottery.recentWinner()
    assert lottery.balance() == 0
    assert get_account(index=expected).balance() == balance_of_account + balance_of_contract