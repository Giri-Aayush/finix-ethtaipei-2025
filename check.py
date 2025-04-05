#!/usr/bin/env python3
"""
Celo Transaction Script

This script sends transactions on the Celo blockchain using a private key stored in an .env file.
It supports both Celo Mainnet and Alfajores testnet.
"""

import os
import argparse
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables from .env file
load_dotenv()

# Celo network RPC endpoints
CELO_NETWORKS = {
    "mainnet": {
        "public": "https://forno.celo.org",
        "alchemy": "https://celo-mainnet.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"
    },
    "alfajores": {
        "public": "https://alfajores-forno.celo-testnet.org",
        "alchemy": "https://celo-alfajores.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"
    }
}

def get_web3(network="mainnet", use_alchemy=False):
    """
    Initialize and return a Web3 instance connected to the specified Celo network.
    
    Args:
        network: 'mainnet' or 'alfajores'
        use_alchemy: Whether to use Alchemy RPC instead of public RPC
        
    Returns:
        Web3 instance connected to the specified network
    """
    if network not in CELO_NETWORKS:
        raise ValueError(f"Unknown network: {network}. Choose 'mainnet' or 'alfajores'")
    
    rpc_type = "alchemy" if use_alchemy else "public"
    rpc_url = CELO_NETWORKS[network][rpc_type]
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to Celo {network} at {rpc_url}")
    
    print(f"Connected to Celo {network} using {rpc_type} RPC")
    return w3

def send_transaction(to_address, amount, token_type="CELO", network="mainnet", use_alchemy=False):
    """
    Send a transaction on the Celo network.
    
    Args:
        to_address: Recipient address
        amount: Amount to send
        token_type: 'CELO', 'cUSD', 'cEUR', etc.
        network: 'mainnet' or 'alfajores'
        use_alchemy: Whether to use Alchemy RPC
    """
    # Get private key from environment variable
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable not set")
    
    # Ensure private key has 0x prefix
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    
    # Connect to Celo network
    w3 = get_web3(network, use_alchemy)
    
    # Load account from private key
    account = Account.from_key(private_key)
    address = account.address
    print(f"Using account: {address}")
    
    # Check if we're sending native CELO or a stablecoin
    if token_type == "CELO":
        # Get account balance
        balance_wei = w3.eth.get_balance(address)
        balance = w3.from_wei(balance_wei, 'ether')
        print(f"CELO Balance: {balance} CELO")
        
        # Convert CELO to wei
        amount_wei = w3.to_wei(amount, 'ether')
        
        # Check if we have enough balance
        if amount_wei > balance_wei:
            raise ValueError(f"Insufficient balance: {balance} CELO available, trying to send {amount} CELO")
        
        # Get the current nonce for the account
        nonce = w3.eth.get_transaction_count(address)
        
        # Estimate gas price (Celo doesn't use EIP-1559)
        gas_price = w3.eth.gas_price
        
        # Build transaction for native CELO transfer
        tx = {
            'from': address,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,  # Standard gas limit for basic transfers
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': w3.eth.chain_id
        }
    else:
        # For stablecoins (cUSD, cEUR, etc.)
        # We need to interact with their respective token contracts
        token_addresses = {
            "cUSD": {
                "mainnet": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
                "alfajores": "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1"
            },
            "cEUR": {
                "mainnet": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
                "alfajores": "0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F"
            }
        }
        
        if token_type not in token_addresses:
            raise ValueError(f"Unsupported token type: {token_type}. Supported tokens are CELO, cUSD, cEUR")
        
        token_address = token_addresses[token_type][network]
        
        # ERC-20 ABI for transfer function
        token_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "success", "type": "bool"}],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Create contract instance
        token_contract = w3.eth.contract(address=token_address, abi=token_abi)
        
        # Get token balance
        token_balance = token_contract.functions.balanceOf(address).call()
        token_balance_formatted = token_balance / 10**18  # Assuming 18 decimals for Celo tokens
        print(f"{token_type} Balance: {token_balance_formatted} {token_type}")
        
        # Convert amount to token units (with 18 decimals)
        amount_in_token_units = int(amount * 10**18)
        
        # Check if we have enough balance
        if amount_in_token_units > token_balance:
            raise ValueError(f"Insufficient balance: {token_balance_formatted} {token_type} available, trying to send {amount} {token_type}")
        
        # Get the current nonce for the account
        nonce = w3.eth.get_transaction_count(address)
        
        # Estimate gas
        gas_price = w3.eth.gas_price
        
        # Build transaction
        transfer_txn = token_contract.functions.transfer(
            to_address,
            amount_in_token_units
        ).build_transaction({
            'from': address,
            'gas': 100000,  # Higher gas limit for contract interaction
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': w3.eth.chain_id
        })
        
        tx = transfer_txn
    
    # Sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = w3.to_hex(tx_hash)
    
    print(f"Transaction sent: {tx_hash_hex}")
    
    # Provide the appropriate block explorer link
    if network == "mainnet":
        print(f"Monitor at: https://explorer.celo.org/mainnet/tx/{tx_hash_hex}")
    else:
        print(f"Monitor at: https://explorer.celo.org/alfajores/tx/{tx_hash_hex}")
    
    return tx_hash_hex

def interact_with_contract(contract_address, function_name, function_args, abi_path, value=0, network="mainnet", use_alchemy=False):
    """
    Interact with a smart contract on the Celo network.
    
    Args:
        contract_address: Contract address
        function_name: Name of the function to call
        function_args: List of arguments to pass to the function
        abi_path: Path to the contract ABI JSON file
        value: CELO amount to send with the transaction (optional)
        network: 'mainnet' or 'alfajores'
        use_alchemy: Whether to use Alchemy RPC
    """
    # Get private key from environment variable
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable not set")
    
    # Ensure private key has 0x prefix
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    
    # Connect to Celo network
    w3 = get_web3(network, use_alchemy)
    
    # Load account from private key
    account = Account.from_key(private_key)
    address = account.address
    print(f"Using account: {address}")
    
    # Load ABI
    with open(abi_path, 'r') as f:
        import json
        abi = json.load(f)
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Get the contract function
    contract_function = getattr(contract.functions, function_name)
    
    # Call the function with arguments
    function_call = contract_function(*function_args)
    
    # Check if function is view/pure (doesn't modify state)
    try:
        # Try to get function ABI to determine if it's a view function
        function_abi = next(
            (item for item in abi if item.get('name') == function_name),
            None
        )
        
        is_view = function_abi and (
            function_abi.get('stateMutability') in ['view', 'pure'] or 
            function_abi.get('constant') == True
        )
        
        if is_view:
            # Function is a view/pure function, just call it and return the result
            result = function_call.call()
            print(f"Function result: {result}")
            return result
    except:
        # If we couldn't determine from ABI, try calling it
        try:
            result = function_call.call()
            print(f"Function result: {result}")
            return result
        except:
            # If calling fails, it's likely a state-changing function
            pass
    
    # Function is a state-changing function, build and send a transaction
    value_wei = w3.to_wei(value, 'ether')
    
    # Get the current nonce for the account
    nonce = w3.eth.get_transaction_count(address)
    
    # Get gas price
    gas_price = w3.eth.gas_price
    
    # Build transaction
    tx = function_call.build_transaction({
        'from': address,
        'value': value_wei,
        'gas': 2000000,  # Higher initial gas limit for contract calls
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': w3.eth.chain_id
    })
    
    # Try to estimate gas (to avoid out-of-gas errors)
    try:
        gas_estimate = w3.eth.estimate_gas(tx)
        tx['gas'] = gas_estimate
    except Exception as e:
        print(f"Warning: Failed to estimate gas. Using default: {tx['gas']}")
        print(f"Error details: {str(e)}")
    
    # Sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = w3.to_hex(tx_hash)
    
    print(f"Transaction sent: {tx_hash_hex}")
    
    # Provide the appropriate block explorer link
    if network == "mainnet":
        print(f"Monitor at: https://explorer.celo.org/mainnet/tx/{tx_hash_hex}")
    else:
        print(f"Monitor at: https://explorer.celo.org/alfajores/tx/{tx_hash_hex}")
    
    return tx_hash_hex

def sign_message(message, network="mainnet", use_alchemy=False):
    """
    Sign a message using the private key from environment variable.
    
    Args:
        message: Message to sign
        network: 'mainnet' or 'alfajores' (just for display)
        use_alchemy: Whether to use Alchemy RPC (just for display)
    """
    # Get private key from environment variable
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable not set")
    
    # Ensure private key has 0x prefix
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    
    # Initialize web3
    w3 = get_web3(network, use_alchemy)
    
    # Load account from private key
    account = Account.from_key(private_key)
    print(f"Using account: {account.address}")
    
    # Sign the message
    from eth_account.messages import encode_defunct
    encoded_message = encode_defunct(text=message)
    signed_message = account.sign_message(encoded_message)
    
    # Print signature information
    print(f"Message: {message}")
    print(f"Message Hash: {w3.to_hex(signed_message.message_hash)}")
    print(f"Signature: {w3.to_hex(signed_message.signature)}")
    print(f"r: {signed_message.r}")
    print(f"s: {signed_message.s}")
    print(f"v: {signed_message.v}")
    
    return {
        'message': message,
        'message_hash': w3.to_hex(signed_message.message_hash),
        'signature': w3.to_hex(signed_message.signature),
        'r': signed_message.r,
        's': signed_message.s,
        'v': signed_message.v
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Celo Transaction Script")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Send transaction command
    send_parser = subparsers.add_parser("send", help="Send tokens on Celo")
    send_parser.add_argument("to_address", help="Recipient address")
    send_parser.add_argument("amount", type=float, help="Amount to send")
    send_parser.add_argument("--token", default="CELO", choices=["CELO", "cUSD", "cEUR"], 
                             help="Token type (CELO, cUSD, or cEUR)")
    send_parser.add_argument("--network", default="mainnet", choices=["mainnet", "alfajores"], 
                             help="Celo network to use")
    send_parser.add_argument("--use-alchemy", action="store_true", 
                             help="Use Alchemy RPC instead of public RPC")
    
    # Contract interaction command
    contract_parser = subparsers.add_parser("contract", help="Interact with a smart contract")
    contract_parser.add_argument("address", help="Contract address")
    contract_parser.add_argument("function", help="Function name to call")
    contract_parser.add_argument("--args", nargs="*", default=[], help="Function arguments")
    contract_parser.add_argument("--abi", required=True, help="Path to contract ABI JSON file")
    contract_parser.add_argument("--value", type=float, default=0, 
                                help="CELO value to send with transaction")
    contract_parser.add_argument("--network", default="mainnet", choices=["mainnet", "alfajores"], 
                                help="Celo network to use")
    contract_parser.add_argument("--use-alchemy", action="store_true", 
                                help="Use Alchemy RPC instead of public RPC")
    
    # Sign message command
    sign_parser = subparsers.add_parser("sign", help="Sign a message")
    sign_parser.add_argument("message", help="Message to sign")
    sign_parser.add_argument("--network", default="mainnet", choices=["mainnet", "alfajores"], 
                            help="Celo network to use (for display only)")
    sign_parser.add_argument("--use-alchemy", action="store_true", 
                            help="Use Alchemy RPC instead of public RPC (for display only)")
    
    args = parser.parse_args()
    
    if args.command == "send":
        send_transaction(args.to_address, args.amount, args.token, args.network, args.use_alchemy)
    elif args.command == "contract":
        # Convert string arguments to appropriate types when possible
        processed_args = []
        for arg in args.args:
            # Try to convert to int or float if it looks like a number
            if arg.isdigit():
                processed_args.append(int(arg))
            elif arg.replace('.', '', 1).isdigit() and arg.count('.') < 2:
                processed_args.append(float(arg))
            elif arg.lower() in ['true', 'false']:
                processed_args.append(arg.lower() == 'true')
            else:
                processed_args.append(arg)
                
        interact_with_contract(args.address, args.function, processed_args, 
                              args.abi, args.value, args.network, args.use_alchemy)
    elif args.command == "sign":
        sign_message(args.message, args.network, args.use_alchemy)
    else:
        parser.print_help()