     
import os
import json
import argparse
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Supply, Withdraw, Set Collateral, Borrow, or Repay on Aave')
parser.add_argument('--action', type=str, required=True, 
                    choices=['supply', 'withdraw', 'set-collateral', 'borrow', 'repay'], 
                    help='Action to perform: "supply", "withdraw", "set-collateral", "borrow", or "repay"')
parser.add_argument('--amount', type=float, default=0, 
                    help='Amount of CELO/USDC to supply/withdraw/borrow/repay (e.g., 0.05). Use 0 for withdraw/repay all. Not used for set-collateral.')
parser.add_argument('--use-as-collateral', type=str, choices=['true', 'false'], default='true',
                    help='Whether to use CELO as collateral (true/false). Only used with set-collateral action.')
args = parser.parse_args()

# Get private key from .env file
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("Private key not found in .env file")

# Celo RPC endpoint
CELO_RPC_URL = "https://celo-mainnet.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"  # Mainnet

# Connect to Celo network
web3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))
if not web3.is_connected():
    raise ConnectionError("Failed to connect to Celo network")

# Contract addresses
LENDING_POOL_ADDRESS = "0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402"  # Aave lending pool
CELO_TOKEN_ADDRESS = "0x471EcE3750Da237f93B8E339c536989b8978a438"    # CELO token address
USDC_TOKEN_ADDRESS = "0xcebA9300f2b948710d2653dD7B07f33A8B32118C"    # USDC token address

# Explorer URL for transaction tracking
EXPLORER_URL = "https://celoscan.io/tx/0x"

# ABI for ERC20 tokens (CELO)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ABI for the LendingPool contract
LENDING_POOL_ABI = [
    # Supply function
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "onBehalfOf", "type": "address"},
            {"internalType": "uint16", "name": "referralCode", "type": "uint16"}
        ],
        "name": "supply",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Withdraw function
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "to", "type": "address"}
        ],
        "name": "withdraw",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Set user use reserve as collateral function
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "bool", "name": "useAsCollateral", "type": "bool"}
        ],
        "name": "setUserUseReserveAsCollateral",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Borrow function
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "interestRateMode", "type": "uint256"},
            {"internalType": "uint16", "name": "referralCode", "type": "uint16"},
            {"internalType": "address", "name": "onBehalfOf", "type": "address"}
        ],
        "name": "borrow",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Repay function
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "interestRateMode", "type": "uint256"},
            {"internalType": "address", "name": "onBehalfOf", "type": "address"}
        ],
        "name": "repay",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def borrow_usdc(from_address, amount_in_usdc):
    """
    Function to borrow USDC from Aave
    """
    # Create lending pool contract instance
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    
    # Convert USDC amount to Wei (USDC has 6 decimals)
    amount_in_wei = int(amount_in_usdc * 10**6)
    
    # Call the borrow function
    print(f"Borrowing {amount_in_usdc} USDC...")
    borrow_tx = lending_pool.functions.borrow(
        USDC_TOKEN_ADDRESS,   # asset address (USDC token)
        amount_in_wei,        # amount to borrow
        2,                    # interest rate mode (2 = variable)
        0,                    # referral code
        from_address          # on behalf of (our own address)
    ).build_transaction({
        'from': from_address,
        'gas': 400000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the borrow transaction
    signed_borrow_tx = web3.eth.account.sign_transaction(borrow_tx, PRIVATE_KEY)
    borrow_tx_hash = web3.eth.send_raw_transaction(signed_borrow_tx.raw_transaction)
    borrow_tx_hash_hex = borrow_tx_hash.hex()
    print(f"Borrow transaction hash: {borrow_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{borrow_tx_hash_hex}")
    
    # Wait for the borrow transaction to be mined
    borrow_receipt = web3.eth.wait_for_transaction_receipt(borrow_tx_hash)
    print(f"Borrow transaction status: {borrow_receipt['status']}")
    
    if borrow_receipt['status'] == 1:
        print(f"Successfully borrowed {amount_in_usdc} USDC from Aave on Celo!")
    else:
        print("Borrow transaction failed.")

def repay_usdc(from_address, amount_in_usdc):
    """
    Function to repay USDC to Aave
    """
    # Create contract instances
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    usdc_token = web3.eth.contract(address=USDC_TOKEN_ADDRESS, abi=ERC20_ABI)
    
    # Convert USDC amount to Wei (USDC has 6 decimals)
    # For repaying all, use uint256 max value
    if amount_in_usdc == 0:
        amount_in_wei = 2**256 - 1  # max uint256 value
        print("Repaying all USDC...")
    else:
        amount_in_wei = int(amount_in_usdc * 10**6)
        print(f"Repaying {amount_in_usdc} USDC...")
    
    # First, check and approve USDC for the lending pool
    usdc_balance = usdc_token.functions.balanceOf(from_address).call()
    print(f"USDC Balance: {usdc_balance / 10**6} USDC")
    
    if amount_in_wei != 2**256 - 1 and usdc_balance < amount_in_wei:
        print(f"Not enough USDC balance. Have {usdc_balance / 10**6} USDC, need {amount_in_usdc} USDC")
        return
    
    # Approve USDC for lending pool
    print("Approving USDC for LendingPool...")
    approve_tx = usdc_token.functions.approve(
        LENDING_POOL_ADDRESS,
        amount_in_wei if amount_in_wei != 2**256 - 1 else usdc_balance  # Approve only what we have for max value
    ).build_transaction({
        'from': from_address,
        'gas': 200000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the approval transaction
    signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
    approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
    approve_tx_hash_hex = approve_tx_hash.hex()
    print(f"Approval transaction hash: {approve_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{approve_tx_hash_hex}")
    
    # Wait for the approval transaction to be mined
    approve_receipt = web3.eth.wait_for_transaction_receipt(approve_tx_hash)
    print(f"Approval transaction status: {approve_receipt['status']}")
    
    if approve_receipt['status'] != 1:
        raise Exception("Approval transaction failed")
    
    # Now call the repay function
    print("Repaying USDC to Aave...")
    repay_tx = lending_pool.functions.repay(
        USDC_TOKEN_ADDRESS,   # asset address (USDC token)
        amount_in_wei,        # amount to repay
        2,                    # interest rate mode (2 = variable)
        from_address          # on behalf of (our own address)
    ).build_transaction({
        'from': from_address,
        'gas': 300000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the repay transaction
    signed_repay_tx = web3.eth.account.sign_transaction(repay_tx, PRIVATE_KEY)
    repay_tx_hash = web3.eth.send_raw_transaction(signed_repay_tx.raw_transaction)
    repay_tx_hash_hex = repay_tx_hash.hex()
    print(f"Repay transaction hash: {repay_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{repay_tx_hash_hex}")
    
    # Wait for the repay transaction to be mined
    repay_receipt = web3.eth.wait_for_transaction_receipt(repay_tx_hash)
    print(f"Repay transaction status: {repay_receipt['status']}")
    
    if repay_receipt['status'] == 1:
        if amount_in_wei == 2**256 - 1:
            print("Successfully repaid all USDC to Aave on Celo!")
        else:
            print(f"Successfully repaid {amount_in_usdc} USDC to Aave on Celo!")
    else:
        print("Repay transaction failed.")
        
def set_collateral(from_address, use_as_collateral):
    """
    Function to set CELO as collateral or not in Aave
    """
    # Create lending pool contract instance
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    
    # Call the setUserUseReserveAsCollateral function
    print(f"Setting CELO to use as collateral: {use_as_collateral}")
    set_collateral_tx = lending_pool.functions.setUserUseReserveAsCollateral(
        CELO_TOKEN_ADDRESS,  # asset address (CELO token)
        use_as_collateral    # whether to use as collateral or not
    ).build_transaction({
        'from': from_address,
        'gas': 200000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the set collateral transaction
    signed_set_collateral_tx = web3.eth.account.sign_transaction(set_collateral_tx, PRIVATE_KEY)
    set_collateral_tx_hash = web3.eth.send_raw_transaction(signed_set_collateral_tx.raw_transaction)
    set_collateral_tx_hash_hex = set_collateral_tx_hash.hex()
    print(f"Set collateral transaction hash: {set_collateral_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{set_collateral_tx_hash_hex}")
    
    # Wait for the set collateral transaction to be mined
    set_collateral_receipt = web3.eth.wait_for_transaction_receipt(set_collateral_tx_hash)
    print(f"Set collateral transaction status: {set_collateral_receipt['status']}")
    
    if set_collateral_receipt['status'] == 1:
        if use_as_collateral:
            print("Successfully set CELO to be used as collateral in Aave!")
        else:
            print("Successfully set CELO to NOT be used as collateral in Aave!")
    else:
        print("Set collateral transaction failed.")
   

def supply_celo(from_address, amount_in_wei):
    """
    Function to supply CELO to Aave
    """
    # Create contract instances
    celo_token = web3.eth.contract(address=CELO_TOKEN_ADDRESS, abi=ERC20_ABI)
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    
    # Check token balance for the wrapped CELO
    token_balance = celo_token.functions.balanceOf(from_address).call()
    print(f"Wrapped CELO Balance: {web3.from_wei(token_balance, 'ether')} CELO")
    
    # Check if we have enough wrapped CELO
    if token_balance < amount_in_wei:
        native_balance = web3.eth.get_balance(from_address)
        print(f"Native CELO Balance: {web3.from_wei(native_balance, 'ether')} CELO")
        print("Not enough wrapped CELO. You need to convert native CELO to wrapped CELO first.")
        print("This would require additional steps using the CELO wrapper contract.")
        return
    
    # 1. First, approve the CELO token for the lending pool
    print("Approving CELO token for LendingPool...")
    approve_tx = celo_token.functions.approve(
        LENDING_POOL_ADDRESS,
        amount_in_wei
    ).build_transaction({
        'from': from_address,
        'gas': 200000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the approval transaction
    signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
    approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
    approve_tx_hash_hex = approve_tx_hash.hex()
    print(f"Approval transaction hash: {approve_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{approve_tx_hash_hex}")
    
    # Wait for the approval transaction to be mined
    approve_receipt = web3.eth.wait_for_transaction_receipt(approve_tx_hash)
    print(f"Approval transaction status: {approve_receipt['status']}")
    
    if approve_receipt['status'] != 1:
        raise Exception("Approval transaction failed")
    
    # 2. Now, call the supply function
    print("Supplying CELO to Aave...")
    supply_tx = lending_pool.functions.supply(
        CELO_TOKEN_ADDRESS,  # asset address (wrapped CELO token)
        amount_in_wei,       # amount
        from_address,        # onBehalfOf (our own address)
        0                    # referralCode
    ).build_transaction({
        'from': from_address,
        'gas': 300000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the supply transaction
    signed_supply_tx = web3.eth.account.sign_transaction(supply_tx, PRIVATE_KEY)
    supply_tx_hash = web3.eth.send_raw_transaction(signed_supply_tx.raw_transaction)
    supply_tx_hash_hex = supply_tx_hash.hex()
    print(f"Supply transaction hash: {supply_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{supply_tx_hash_hex}")
    
    # Wait for the supply transaction to be mined
    supply_receipt = web3.eth.wait_for_transaction_receipt(supply_tx_hash)
    print(f"Supply transaction status: {supply_receipt['status']}")
    
    if supply_receipt['status'] == 1:
        amount_in_celo = web3.from_wei(amount_in_wei, 'ether')
        print(f"Successfully supplied {amount_in_celo} CELO to Aave on Celo!")
        print("You received aCELO tokens in return, representing your deposit position.")
    else:
        print("Supply transaction failed.")

def withdraw_celo(from_address, amount_in_wei):
    """
    Function to withdraw CELO from Aave
    """
    # Create lending pool contract instance
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    
    # For withdrawing all, use uint256 max value
    if amount_in_wei == 0:
        amount_in_wei = 2**256 - 1  # max uint256 value
        print("Withdrawing all CELO")
    
    # Call the withdraw function directly
    print("Withdrawing CELO from Aave...")
    withdraw_tx = lending_pool.functions.withdraw(
        CELO_TOKEN_ADDRESS,  # asset address (CELO token)
        amount_in_wei,       # amount to withdraw
        from_address         # recipient address (our own address)
    ).build_transaction({
        'from': from_address,
        'gas': 300000,
        'maxFeePerGas': web3.to_wei('25.001', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('25.001', 'gwei'),
        'type': 2,  # EIP-1559 transaction
        'nonce': web3.eth.get_transaction_count(from_address),
    })
    
    # Sign and send the withdraw transaction
    signed_withdraw_tx = web3.eth.account.sign_transaction(withdraw_tx, PRIVATE_KEY)
    withdraw_tx_hash = web3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
    withdraw_tx_hash_hex = withdraw_tx_hash.hex()
    print(f"Withdrawal transaction hash: {withdraw_tx_hash_hex}")
    print(f"View on explorer: {EXPLORER_URL}{withdraw_tx_hash_hex}")
    
    # Wait for the withdrawal transaction to be mined
    withdraw_receipt = web3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
    print(f"Withdrawal transaction status: {withdraw_receipt['status']}")
    
    if withdraw_receipt['status'] == 1:
        if amount_in_wei == 2**256 - 1:
            print(f"Successfully withdrew all CELO from Aave on Celo!")
        else:
            amount_in_celo = web3.from_wei(amount_in_wei, 'ether')
            print(f"Successfully withdrew {amount_in_celo} CELO from Aave on Celo!")
        print("Your aCELO tokens have been returned in exchange for CELO.")
    else:
        print("Withdrawal transaction failed.")

def main():
    # Set up account from private key
    account = web3.eth.account.from_key(PRIVATE_KEY)
    from_address = account.address
    print(f"Using account: {from_address}")
    
    # Get action and parameters from command line args
    action = args.action
    
    print(f"Action: {action.upper()}")
    if action == "supply":
        amount_in_celo = args.amount
        if amount_in_celo <= 0:
            print("Error: Amount must be greater than 0 for supply action")
            return
        amount_in_wei = web3.to_wei(amount_in_celo, 'ether')
        print(f"Amount to supply: {amount_in_celo} CELO ({amount_in_wei} wei)")
        supply_celo(from_address, amount_in_wei)
    elif action == "withdraw":
        amount_in_celo = args.amount
        amount_in_wei = web3.to_wei(amount_in_celo, 'ether') if amount_in_celo > 0 else 0
        if amount_in_celo == 0:
            print("Amount to withdraw: ALL CELO")
        else:
            print(f"Amount to withdraw: {amount_in_celo} CELO ({amount_in_wei} wei)")
        withdraw_celo(from_address, amount_in_wei)
    elif action == "set-collateral":
        use_as_collateral_str = args.use_as_collateral.lower()
        use_as_collateral = True if use_as_collateral_str == 'true' else False
        print(f"Setting CELO to use as collateral: {use_as_collateral}")
        set_collateral(from_address, use_as_collateral)
    elif action == "borrow":
        amount_in_usdc = args.amount
        if amount_in_usdc <= 0:
            print("Error: Amount must be greater than 0 for borrow action")
            return
        print(f"Amount to borrow: {amount_in_usdc} USDC")
        borrow_usdc(from_address, amount_in_usdc)
    elif action == "repay":
        amount_in_usdc = args.amount
        if amount_in_usdc == 0:
            print("Amount to repay: ALL USDC")
        else:
            print(f"Amount to repay: {amount_in_usdc} USDC")
        repay_usdc(from_address, amount_in_usdc)
    else:
        print(f"Invalid action: {action}. Use 'supply', 'withdraw', 'set-collateral', 'borrow', or 'repay'.")

if __name__ == "__main__":
    main()