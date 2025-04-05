#!/usr/bin/env python3
"""
Celo Account & Wallet Info Checker - Fixed for Alfajores Testnet

This script provides comprehensive functionality to check information about Celo accounts:
- Wallet balances (CELO, cUSD, cEUR, etc.)
- Account activity / transaction history
- Tokens held by a wallet
- Account metadata
- Validator/voter status and staking information
"""

import requests
import json
import argparse
from web3 import Web3
from datetime import datetime
import traceback

# Initialize connection to Celo networks
CELO_MAINNET_URL = "https://forno.celo.org"  # Using public RPC endpoint
CELO_ALFAJORES_URL = "https://alfajores-forno.celo-testnet.org"  # Using public RPC endpoint
CUSTOM_MAINNET_RPC = "https://celo-mainnet.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"
CUSTOM_ALFAJORES_RPC = "https://celo-alfajores.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"

# Mainnet contract addresses
MAINNET = {
    "CELO": "0x471EcE3750Da237f93B8E339c536989b8978a438",
    "CUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
    "CEUR": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
    "ACCOUNTS": "0x7d21685C17607338b313a7174bAb6620baD0aaB7",
    "VALIDATORS": "0xaEb865bCa93DdC8F47b8e29F40C5399cE34d0C58",
    "ELECTION": "0x8D6677192144292870907E3Fa8A5527fE55A7ff6",
    "LOCKEDGOLD": "0x6cC083Aed9e3ebe302A6336dBC7c921C9f03349E"
}

# Alfajores testnet contract addresses
ALFAJORES = {
    "CELO": "0xF194afDf50B03e69Bd7D057c1Aa9e10c9954E4C9",
    "CUSD": "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1",
    "CEUR": "0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F",
    "ACCOUNTS": "0xed7f51A34B4e71fbE69B3091FcF879cD14bD73A9",
    "VALIDATORS": "0xAF9f549774DcC5f7cE46c9A9aE7913Fe7E7a889C",
    "ELECTION": "0x1c3eDf937CFc2F6F51784D20DEB1AF1F9a8655fA",
    "LOCKEDGOLD": "0x6a4CC5693DC5BFA3799C699F85E766254eFa9a10"
}

# Contract ABI for ERC-20 tokens
ERC20_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
]''')

# Contract ABI for Accounts
ACCOUNTS_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"getName","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"getMetadataURL","outputs":[{"name":"","type":"string"}],"type":"function"}
]''')

# Contract ABI for Validators and Election
VALIDATORS_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"isValidator","outputs":[{"name":"","type":"bool"}],"type":"function"}
]''')

ELECTION_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"hasActivatablePendingVotes","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"getTotalVotesByAccount","outputs":[{"name":"","type":"uint256"}],"type":"function"}
]''')

LOCKEDGOLD_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"getAccountTotalLockedGold","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"getAccountNonvotingLockedGold","outputs":[{"name":"","type":"uint256"}],"type":"function"}
]''')


class CeloAccountChecker:
    def __init__(self, network="mainnet", custom_rpc=None):
        """Initialize the CeloAccountChecker with the selected network."""
        self.network = network.lower()
        
        # Set RPC URL based on network and custom RPC if provided
        if self.network == "mainnet":
            self.rpc_url = custom_rpc or CUSTOM_MAINNET_RPC or CELO_MAINNET_URL
            self.block_explorer = "https://explorer.celo.org"
            self.contracts = MAINNET
        else:  # alfajores
            self.rpc_url = custom_rpc or CUSTOM_ALFAJORES_RPC or CELO_ALFAJORES_URL
            self.block_explorer = "https://alfajores.celoscan.io"
            self.celoscan_api = "https://api-alfajores.celoscan.io/api"
            self.contracts = ALFAJORES
            
        print(f"Connecting to {self.network} at {self.rpc_url}")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Celo {self.network}")
        else:
            print(f"Connected to Celo {self.network}, chain ID: {self.w3.eth.chain_id}")
        
        # Initialize contracts - safely with try/except for each
        try:
            self.celo_token = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["CELO"]), 
                abi=ERC20_ABI
            )
            print(f"CELO token contract initialized: {self.contracts['CELO']}")
        except Exception as e:
            print(f"Warning: Failed to initialize CELO token contract: {e}")
            self.celo_token = None
            
        try:
            self.cusd_token = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["CUSD"]), 
                abi=ERC20_ABI
            )
            print(f"cUSD token contract initialized: {self.contracts['CUSD']}")
        except Exception as e:
            print(f"Warning: Failed to initialize cUSD token contract: {e}")
            self.cusd_token = None
            
        try:
            self.ceur_token = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["CEUR"]), 
                abi=ERC20_ABI
            )
            print(f"cEUR token contract initialized: {self.contracts['CEUR']}")
        except Exception as e:
            print(f"Warning: Failed to initialize cEUR token contract: {e}")
            self.ceur_token = None
            
        try:
            self.accounts = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["ACCOUNTS"]), 
                abi=ACCOUNTS_ABI
            )
            print(f"Accounts contract initialized: {self.contracts['ACCOUNTS']}")
        except Exception as e:
            print(f"Warning: Failed to initialize Accounts contract: {e}")
            self.accounts = None
            
        try:
            self.validators = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["VALIDATORS"]), 
                abi=VALIDATORS_ABI
            )
            print(f"Validators contract initialized: {self.contracts['VALIDATORS']}")
        except Exception as e:
            print(f"Warning: Failed to initialize Validators contract: {e}")
            self.validators = None
            
        try:
            self.election = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["ELECTION"]), 
                abi=ELECTION_ABI
            )
            print(f"Election contract initialized: {self.contracts['ELECTION']}")
        except Exception as e:
            print(f"Warning: Failed to initialize Election contract: {e}")
            self.election = None
            
        try:
            self.locked_gold = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts["LOCKEDGOLD"]), 
                abi=LOCKEDGOLD_ABI
            )
            print(f"LockedGold contract initialized: {self.contracts['LOCKEDGOLD']}")
        except Exception as e:
            print(f"Warning: Failed to initialize LockedGold contract: {e}")
            self.locked_gold = None
    
    def check_wallet_balance(self, address):
        """Check balances of CELO, cUSD, cEUR for a given address."""
        try:
            address = Web3.to_checksum_address(address)
        except:
            return {"error": f"Invalid address format: {address}"}
            
        result = {}
        
        # Get native CELO balance
        try:
            celo_balance = self.w3.eth.get_balance(address)
            result["CELO"] = self.w3.from_wei(celo_balance, "ether")
        except Exception as e:
            result["CELO"] = f"Error: {str(e)}"
        
        # Get cUSD balance
        if self.cusd_token:
            try:
                cusd_balance = self.cusd_token.functions.balanceOf(address).call()
                cusd_decimals = self.cusd_token.functions.decimals().call()
                result["cUSD"] = cusd_balance / 10**cusd_decimals
            except Exception as e:
                result["cUSD"] = f"Error: {str(e)}"
        
        # Get cEUR balance
        if self.ceur_token:
            try:
                ceur_balance = self.ceur_token.functions.balanceOf(address).call()
                ceur_decimals = self.ceur_token.functions.decimals().call()
                result["cEUR"] = ceur_balance / 10**ceur_decimals
            except Exception as e:
                result["cEUR"] = f"Error: {str(e)}"
        
        return result
    
    def get_transaction_history(self, address, max_count=10):
        """Get transaction history for a given address."""
        try:
            address = Web3.to_checksum_address(address)
        except:
            return {"error": f"Invalid address format: {address}"}
        
        transactions = []
        
        # Get most recent block number
        try:
            latest_block = self.w3.eth.block_number
            print(f"Current block: {latest_block}")
            
            # Scan recent blocks for transactions involving this address
            scan_blocks = min(10, latest_block)  # Limit scan to last 1000 blocks
            print(f"Scanning the last {scan_blocks} blocks for transactions...")
            
            tx_count = 0
            for block_num in range(latest_block, latest_block - scan_blocks, -1):
                if tx_count >= max_count:
                    break
                    
                try:
                    block = self.w3.eth.get_block(block_num, full_transactions=True)
                    
                    for tx in block['transactions']:
                        # Check if the transaction involves our address
                        if (tx.get('from', '').lower() == address.lower() or 
                            tx.get('to', '').lower() == address.lower()):
                            
                            tx_count += 1
                            
                            try:
                                receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                                tx_status = "Success" if receipt.get('status') == 1 else "Failed"
                            except:
                                tx_status = "Unknown"
                                
                            transactions.append({
                                "hash": tx['hash'].hex(),
                                "block_number": tx['blockNumber'],
                                "from": tx.get('from', 'Unknown'),
                                "to": tx.get('to', 'Contract Creation'),
                                "value": self.w3.from_wei(tx.get('value', 0), "ether"),
                                "timestamp": datetime.fromtimestamp(block['timestamp']),
                                "gas_used": receipt.get('gasUsed', 0) if 'receipt' in locals() else None,
                                "status": tx_status
                            })
                            
                            if tx_count >= max_count:
                                break
                except Exception as e:
                    print(f"Error processing block {block_num}: {e}")
                    continue
                    
            if not transactions:
                print("No transactions found in recent blocks. This account may be inactive.")
                
            return transactions
            
        except Exception as e:
            print(f"Error getting transaction history: {str(e)}")
            return {"error": f"Failed to get transaction history: {str(e)}"}
    
    def list_tokens(self, address):
        """List all tokens held by an address."""
        try:
            address = Web3.to_checksum_address(address)
        except:
            return {"error": f"Invalid address format: {address}"}
            
        tokens = []
        
        # For testnet, we'll list the main tokens we know about
        if self.celo_token:
            try:
                balance = self.celo_token.functions.balanceOf(address).call()
                decimals = 18  # Known CELO decimals
                tokens.append({
                    "name": "Celo",
                    "symbol": "CELO",
                    "address": self.contracts["CELO"],
                    "balance": float(balance) / 10**decimals,
                    "decimals": decimals
                })
            except Exception as e:
                print(f"Warning: Error getting CELO token balance: {e}")
        
        if self.cusd_token:
            try:
                balance = self.cusd_token.functions.balanceOf(address).call()
                decimals = self.cusd_token.functions.decimals().call()
                tokens.append({
                    "name": "Celo Dollar",
                    "symbol": "cUSD",
                    "address": self.contracts["CUSD"],
                    "balance": float(balance) / 10**decimals,
                    "decimals": decimals
                })
            except Exception as e:
                print(f"Warning: Error getting cUSD token balance: {e}")
        
        if self.ceur_token:
            try:
                balance = self.ceur_token.functions.balanceOf(address).call()
                decimals = self.ceur_token.functions.decimals().call()
                tokens.append({
                    "name": "Celo Euro",
                    "symbol": "cEUR",
                    "address": self.contracts["CEUR"],
                    "balance": float(balance) / 10**decimals,
                    "decimals": decimals
                })
            except Exception as e:
                print(f"Warning: Error getting cEUR token balance: {e}")
        
        # Add additional known testnet tokens for Alfajores
        if self.network == "alfajores":
            additional_tokens = [
                {"address": "0xE4D517785D091D3c54818832dB6094bcc2744545", "name": "Celo Brazilian Real", "symbol": "cREAL"},
                {"address": "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B", "name": "USD Coin", "symbol": "USDC"}
            ]
            
            for token_info in additional_tokens:
                try:
                    token_contract = self.w3.eth.contract(
                        address=Web3.to_checksum_address(token_info["address"]),
                        abi=ERC20_ABI
                    )
                    balance = token_contract.functions.balanceOf(address).call()
                    try:
                        decimals = token_contract.functions.decimals().call()
                    except:
                        decimals = 18  # Default
                        
                    tokens.append({
                        "name": token_info["name"],
                        "symbol": token_info["symbol"],
                        "address": token_info["address"],
                        "balance": float(balance) / 10**decimals,
                        "decimals": decimals
                    })
                except Exception as e:
                    print(f"Warning: Error getting {token_info['symbol']} token balance: {e}")
        
        return tokens
    
    def get_account_metadata(self, address):
        """Get account metadata including name and profile URL."""
        try:
            address = Web3.to_checksum_address(address)
        except:
            return {"error": f"Invalid address format: {address}"}
            
        metadata = {"address": address}
        
        if not self.accounts:
            return {"address": address, "error": "Accounts contract not initialized"}
        
        try:
            name = self.accounts.functions.getName(address).call()
            metadata["name"] = name if name else "Not set"
        except Exception as e:
            metadata["name_error"] = f"Failed to get name: {str(e)}"
        
        try:
            metadata_url = self.accounts.functions.getMetadataURL(address).call()
            if metadata_url:
                metadata["metadata_url"] = metadata_url
                try:
                    # Try to fetch the metadata if URL is valid
                    response = requests.get(metadata_url, timeout=5)
                    if response.status_code == 200:
                        try:
                            json_data = response.json()
                            metadata["profile"] = json_data
                        except Exception as e:
                            metadata["metadata_fetch_status"] = f"Invalid JSON: {str(e)}"
                    else:
                        metadata["metadata_fetch_status"] = f"Failed with status code {response.status_code}"
                except Exception as e:
                    metadata["metadata_fetch_status"] = f"Request failed or timed out: {str(e)}"
        except Exception as e:
            metadata["metadata_url_error"] = f"Failed to get metadata URL: {str(e)}"
        
        return metadata
    
    def check_validator_status(self, address):
        """Check if an address is a validator, voter, or has locked CELO for staking."""
        try:
            address = Web3.to_checksum_address(address)
        except:
            return {"error": f"Invalid address format: {address}"}
            
        status = {"address": address}
        
        # Check if address is a validator
        if self.validators:
            try:
                status["is_validator"] = self.validators.functions.isValidator(address).call()
            except Exception as e:
                status["validator_error"] = f"Failed to check validator status: {str(e)}"
        else:
            status["validator_error"] = "Validators contract not initialized"
        
        # Check voting status
        if self.election:
            try:
                status["has_pending_votes"] = self.election.functions.hasActivatablePendingVotes(address).call()
            except Exception as e:
                status["votes_error"] = f"Failed to check pending votes: {str(e)}"
                
            try:
                total_votes = self.election.functions.getTotalVotesByAccount(address).call()
                status["total_votes"] = self.w3.from_wei(total_votes, "ether")
            except Exception as e:
                status["total_votes_error"] = f"Failed to get total votes: {str(e)}"
        else:
            status["election_error"] = "Election contract not initialized"
        
        # Check locked gold status
        if self.locked_gold:
            try:
                total_locked = self.locked_gold.functions.getAccountTotalLockedGold(address).call()
                status["total_locked_celo"] = self.w3.from_wei(total_locked, "ether")
            except Exception as e:
                status["locked_gold_error"] = f"Failed to get total locked gold: {str(e)}"
                
            try:
                nonvoting_locked = self.locked_gold.functions.getAccountNonvotingLockedGold(address).call()
                status["nonvoting_locked_celo"] = self.w3.from_wei(nonvoting_locked, "ether")
                if "total_locked_celo" in status and not isinstance(status["total_locked_celo"], str):
                    status["voting_locked_celo"] = status["total_locked_celo"] - status["nonvoting_locked_celo"]
            except Exception as e:
                status["nonvoting_locked_error"] = f"Failed to get nonvoting locked gold: {str(e)}"
        else:
            status["locked_gold_error"] = "LockedGold contract not initialized"
        
        return status


def main():
    """Main function to demonstrate the Celo Account Checker."""
    parser = argparse.ArgumentParser(description="Celo Account & Wallet Info Checker")
    parser.add_argument("--address", "-a", required=True, help="Celo address to check")
    parser.add_argument("--network", "-n", default="mainnet", choices=["mainnet", "alfajores"], 
                        help="Celo network to connect to")
    parser.add_argument("--check", "-c", choices=["balance", "transactions", "tokens", "metadata", "validator", "all"], 
                        default="all", help="Information to check")
    parser.add_argument("--rpc", help="Custom RPC URL to use")
    
    args = parser.parse_args()
    
    try:
        print("\nInitializing Celo Account Checker...")
        checker = CeloAccountChecker(network=args.network, custom_rpc=args.rpc)
        address = args.address
        
        print(f"\n===== Celo Account Information for {address} on {args.network} =====\n")
        
        if args.check in ["balance", "all"]:
            print("Getting wallet balances...")
            balances = checker.check_wallet_balance(address)
            print("\n📊 Wallet Balances:")
            for token, amount in balances.items():
                print(f"  {token}: {amount}")
            print()
        
        if args.check in ["transactions", "all"]:
            print("Getting transaction history...")
            print("\n📝 Recent Transactions:")
            transactions = checker.get_transaction_history(address, max_count=5)
            if isinstance(transactions, list):
                if transactions:
                    for i, tx in enumerate(transactions):
                        print(f"  {i+1}. {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"     Hash: {tx['hash']}")
                        print(f"     From: {tx['from']}")
                        print(f"     To: {tx['to']}")
                        print(f"     Value: {tx['value']} CELO")
                        print(f"     Status: {tx['status']}")
                        print()
                else:
                    print("  No transactions found in recent blocks")
            else:
                print(f"  Error: {transactions.get('error', 'Unknown error')}")
            print()
        
        if args.check in ["tokens", "all"]:
            print("Getting token holdings...")
            print("\n🪙 Token Holdings:")
            tokens = checker.list_tokens(address)
            if isinstance(tokens, list):
                if tokens:
                    for token in tokens:
                        if token["balance"] > 0:
                            print(f"  {token['symbol']}: {token['balance']} ({token['name']})")
                    
                    # Also show zero balances, but group them
                    zero_tokens = [t for t in tokens if t["balance"] == 0]
                    if zero_tokens:
                        print("\n  Tokens with zero balance:")
                        for token in zero_tokens:
                            print(f"  {token['symbol']} ({token['name']})")
                else:
                    print("  No tokens found")
            else:
                print(f"  Error: {tokens.get('error', 'Unknown error')}")
            print()
        
        if args.check in ["metadata", "all"]:
            print("Getting account metadata...")
            print("\n👤 Account Metadata:")
            metadata = checker.get_account_metadata(address)
            if "error" not in metadata:
                print(f"  Name: {metadata.get('name', 'Not available')}")
                if "metadata_url" in metadata:
                    print(f"  Metadata URL: {metadata['metadata_url']}")
                if "profile" in metadata:
                    print("  Profile Information:")
                    for key, value in metadata["profile"].items():
                        print(f"    {key}: {value}")
                
                # Print any errors
                for key, value in metadata.items():
                    if key.endswith("_error") or key.endswith("_status"):
                        print(f"  Note: {value}")
            else:
                print(f"  Error: {metadata['error']}")
            print()
        
        if args.check in ["validator", "all"]:
            print("Getting validator and staking status...")
            print("\n🔐 Validator and Staking Status:")
            status = checker.check_validator_status(address)
            
            # Print main information
            if "is_validator" in status:
                print(f"  Is Validator: {status['is_validator']}")
            if "has_pending_votes" in status:    
                print(f"  Has Pending Votes: {status['has_pending_votes']}")
            if "total_votes" in status:
                print(f"  Total Votes: {status['total_votes']} CELO")
            if "total_locked_celo" in status:
                print(f"  Total Locked CELO: {status['total_locked_celo']} CELO")
            if "voting_locked_celo" in status:
                print(f"  Voting Locked CELO: {status['voting_locked_celo']} CELO")
            if "nonvoting_locked_celo" in status:
                print(f"  Non-voting Locked CELO: {status['nonvoting_locked_celo']} CELO")
            
            # Print any errors
            error_keys = [k for k in status.keys() if k.endswith("_error")]
            if error_keys:
                print("\n  Notes:")
                for key in error_keys:
                    print(f"  - {status[key]}")
            print()
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()