
from brownie import accounts, Lottery, config, network
from scripts.helper_functions import get_account, get_contract, fund_contract
import time 

def deploy():
    
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract('vrf_coordinator').address,
        get_contract('link_token').address,
        config['networks'][network.show_active()]['fee'],
        config['networks'][network.show_active()]['key_hash'],
        {'from': account},
        publish_source=config['networks'][network.show_active()].get('verify', False)
     )

    print('Contract deployed!') 
    return lottery 
    
def start_lottery():
    account = get_account()
    lottery_contract = Lottery[-1]
    start_lottery_tx = lottery_contract.startLottery({'from': account})
    start_lottery_tx.wait(1)

    print("Started the lottery!")

def enter_lottery():
    account = get_account()
    lottery_contract = Lottery[-1]
    entrance_fee = lottery_contract.getEntranceFee()
    tx = lottery_contract.enter({'from': account, 'value': entrance_fee})
    tx.wait(1)

    print("You entered the lottery!")

def end_lottery():
    account = get_account()
    try:
        lottery_contract = Lottery[-1]
        tx = fund_contract(lottery_contract.address)
        tx.wait(1)
        ending_lottery_tx = lottery_contract.endLottery({'from': account}) 
        ending_lottery_tx.wait(1)

        time.sleep(180)
        print(f'{lottery_contract.recentWinner()} is the new winner!')
    except err:
        print(err)

    print("Lottery ended!")

def main():
    deploy()
    start_lottery()
    enter_lottery()
    end_lottery()