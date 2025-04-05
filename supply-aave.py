import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Contract addresses from the transaction
LENDING_POOL_ADDRESS = "0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402"  # Aave lending pool
CELO_TOKEN_ADDRESS = "0x471EcE3750Da237f93B8E339c536989b8978a438"    # Celo token (wrapped native token)

# Explorer URL for transaction tracking
EXPLORER_URL = "https://celoscan.io/tx/0x"

# ABI for Wrapped CELO (ERC20)
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
    }
]

def main():
    # Set up account from private key
    account = web3.eth.account.from_key(PRIVATE_KEY)
    from_address = account.address
    print(f"Using account: {from_address}")
    
    # Amount to supply - 0.05 CELO (50000000000000000 wei)
    amount = 50000000000000000  # 0.05 CELO
    
    # Create contract instances
    celo_token = web3.eth.contract(address=CELO_TOKEN_ADDRESS, abi=ERC20_ABI)
    lending_pool = web3.eth.contract(address=LENDING_POOL_ADDRESS, abi=LENDING_POOL_ABI)
    
    # Check token balance for the wrapped CELO
    token_balance = celo_token.functions.balanceOf(from_address).call()
    print(f"Wrapped CELO Balance: {web3.from_wei(token_balance, 'ether')} CELO")
    
    # Check if we have enough wrapped CELO
    if token_balance < amount:
        native_balance = web3.eth.get_balance(from_address)
        print(f"Native CELO Balance: {web3.from_wei(native_balance, 'ether')} CELO")
        print("Not enough wrapped CELO. You need to convert native CELO to wrapped CELO first.")
        print("This would require additional steps using the CELO wrapper contract.")
        return
    
    # 1. First, approve the CELO token for the lending pool
    print("Approving CELO token for LendingPool...")
    approve_tx = celo_token.functions.approve(
        LENDING_POOL_ADDRESS,
        amount
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
        amount,              # amount
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
        print("Successfully supplied 0.05 CELO to Aave on Celo!")
        print("You received aCELO tokens in return, representing your deposit position.")
    else:
        print("Supply transaction failed.")

if __name__ == "__main__":
    main()