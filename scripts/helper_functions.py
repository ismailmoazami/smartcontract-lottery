
from brownie import (
     config, 
     network,
     accounts,
     Contract,
     MockV3Aggregator, 
     VRFCoordinatorMock,
     LinkToken, 
     interface,
    )

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local']
LOCAL_FORKED_ENVIRONMENTS = ['mainnet-fork', 'mainnet-fork-dev']

def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or
        network.show_active() in LOCAL_FORKED_ENVIRONMENTS
        ):
        return accounts[0]
    
    return accounts.add(config['wallet']['from_key'])

contract_to_mock = {'eth_usd_price_feed': MockV3Aggregator, "vrf_coordinator": VRFCoordinatorMock,
                    'link_token': LinkToken}

def get_contract(contract_name):
    """ this function return a contract"""

    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mock()
        contract = contract_type[-1]
    else:
        contract_address = config['networks'][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    
    return contract 
    
DECIMALS=8
INITIAL_VALUE=200000000000

def deploy_mock(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {'from': account})
    link_token = LinkToken.deploy({'from': account})
    VRFCoordinatorMock.deploy(link_token.address, {'from': account})

    print("deployed!")

def fund_contract(_contract_address, _account=None, _link_token=None, _fee=100000000000000000):
    account = _account if _account else get_account()
    link_token = _link_token if _link_token else get_contract('link_token')
    tx = link_token.transfer(_contract_address, _fee, {'from': account})
    # link_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_contract.transfer(_contract_address, _fee, {'from': account})
    tx.wait(1)

    print('Contract funded!')
    return tx 