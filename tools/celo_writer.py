# tools/celo_writer.py - Celo blockchain write operations
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
import json
import time
from typing import Dict, Optional

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

# Token addresses on different networks
TOKEN_ADDRESSES = {
    "cUSD": {
        "mainnet": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
        "alfajores": "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1"
    },
    "cEUR": {
        "mainnet": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
        "alfajores": "0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F"
    }
}

# Basic ERC-20 ABI for token transfers
ERC20_ABI = [
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

# Secure session management for temporary private key storage
class TransactionSession:
    """Manages a secure, time-limited transaction session"""
    
    def __init__(self, timeout_seconds: int = 300):
        self.sessions: Dict[str, Dict] = {}
        self.timeout_seconds = timeout_seconds
    
    def create_session(self, public_address: str) -> str:
        """Create a new session for a public address, returns session ID"""
        import hashlib
        session_id = f"session_{int(time.time())}_{hashlib.sha256(public_address.encode()).hexdigest()[:8]}"
        self.sessions[session_id] = {
            "public_address": public_address,
            "created_at": time.time(),
            "private_key": None
        }
        return session_id
    
    def add_private_key(self, session_id: str, private_key: str) -> bool:
        """Add private key to an existing session"""
        if session_id not in self.sessions:
            return False
        
        # Check if session is still valid
        if time.time() - self.sessions[session_id]["created_at"] > self.timeout_seconds:
            self.clear_session(session_id)
            return False
            
        # Store private key in memory only
        self.sessions[session_id]["private_key"] = private_key
        return True
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data if session is valid"""
        if session_id not in self.sessions:
            return None
            
        # Check if session is still valid
        if time.time() - self.sessions[session_id]["created_at"] > self.timeout_seconds:
            self.clear_session(session_id)
            return None
            
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str) -> None:
        """Explicitly clear session data"""
        if session_id in self.sessions:
            # Explicitly clear private key from memory
            if self.sessions[session_id]["private_key"]:
                self.sessions[session_id]["private_key"] = None
            # Remove the session
            del self.sessions[session_id]
    
    def clear_expired_sessions(self) -> None:
        """Clear all expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["created_at"] > self.timeout_seconds:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            self.clear_session(session_id)

# Create a single transaction session manager
tx_session = TransactionSession(timeout_seconds=300)  # 5-minute timeout

def register_celo_writer_tools(mcp: FastMCP):
    """Register all Celo write operation tools with the MCP server."""
    
    @mcp.tool()
    async def create_transaction_session(address: str, ctx: Context = None) -> str:
        """
        Create a new transaction session for a Celo address.
        
        Parameters:
        - address: Celo address to create session for
        
        Returns:
        - Session ID to use for future transactions
        """
        try:
            from web3 import Web3
            
            # Validate address
            try:
                address = Web3.to_checksum_address(address)
            except:
                return f"Invalid address format: {address}"
            
            if ctx:
                ctx.info(f"Creating session for address: {address}")
            
            # Create a new session
            session_id = tx_session.create_session(address)
            
            result = {
                "session_id": session_id,
                "public_address": address,
                "expires_in_seconds": 300,
                "message": "Session created. Use this session_id with add_private_key to enable transactions."
            }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error creating session: {str(e)}"

    @mcp.tool()
    async def add_private_key(session_id: str, private_key: str, ctx: Context = None) -> str:
        """
        Add a private key to an existing transaction session.
        SECURITY WARNING: Private keys provide full access to funds. This tool should only be used
        in secure environments. The private key will be held in memory temporarily.
        
        Parameters:
        - session_id: Session ID from create_transaction_session
        - private_key: Private key for the address (with or without 0x prefix)
        
        Returns:
        - Confirmation message
        """
        try:
            if ctx:
                ctx.info(f"Adding private key to session: {session_id}")
            
            # Ensure private key has 0x prefix
            if not private_key.startswith("0x"):
                private_key = f"0x{private_key}"
            
            # Add the private key to the session
            if not tx_session.add_private_key(session_id, private_key):
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            result = {
                "success": True,
                "message": "Private key added to session. You can now perform transactions until the session expires.",
                "warning": "Your private key is stored in memory and will be automatically cleared after 5 minutes."
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error adding private key: {str(e)}"
            })

    @mcp.tool()
    async def send_celo(session_id: str, to_address: str, amount: float, network: str = "mainnet", use_alchemy: bool = False, ctx: Context = None) -> str:
        """
        Send CELO tokens to another address.
        
        Parameters:
        - session_id: Active session ID
        - to_address: Recipient's Celo address
        - amount: Amount of CELO to send
        - network: 'mainnet' or 'alfajores'
        - use_alchemy: Whether to use Alchemy RPC instead of public RPC
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing CELO transfer request")
                await ctx.report_progress(1, 5)
            
            # Get session data
            session_data = tx_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            if not session_data["private_key"]:
                return format_json_response({
                    "success": False,
                    "error": "No private key added to this session. Use add_private_key first."
                })
            
            if network not in CELO_NETWORKS:
                return format_json_response({
                    "success": False,
                    "error": f"Unknown network: {network}. Choose 'mainnet' or 'alfajores'"
                })
            
            if ctx:
                ctx.info(f"Connecting to Celo {network}")
                await ctx.report_progress(2, 5)
            
            # Connect to Celo network
            rpc_type = "alchemy" if use_alchemy else "public"
            rpc_url = CELO_NETWORKS[network][rpc_type]
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                return format_json_response({
                    "success": False,
                    "error": f"Failed to connect to Celo {network} at {rpc_url}"
                })
            
            # Load account from private key
            account = Account.from_key(session_data["private_key"])
            address = account.address
            
            # Validate recipient address
            try:
                to_address = Web3.to_checksum_address(to_address)
            except:
                return format_json_response({
                    "success": False,
                    "error": f"Invalid recipient address format: {to_address}"
                })
            
            if ctx:
                ctx.info(f"Preparing transaction")
                await ctx.report_progress(3, 5)
            
            # Get account balance
            balance_wei = w3.eth.get_balance(address)
            balance = w3.from_wei(balance_wei, 'ether')
            
            # Convert CELO to wei
            amount_wei = w3.to_wei(amount, 'ether')
            
            # Check if we have enough balance
            if amount_wei > balance_wei:
                return format_json_response({
                    "success": False,
                    "error": f"Insufficient balance: {balance} CELO available, trying to send {amount} CELO"
                })
            
            # Get the current nonce for the account
            nonce = w3.eth.get_transaction_count(address)
            
            # Estimate gas price
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
            
            if ctx:
                ctx.info(f"Signing and sending transaction")
                await ctx.report_progress(4, 5)
            
            # Sign the transaction
            signed_tx = w3.eth.account.sign_transaction(tx, session_data["private_key"])
            
            # Send the transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            
            # Get the block explorer URL
            if network == "mainnet":
                explorer_url = f"https://explorer.celo.org/mainnet/tx/{tx_hash_hex}"
            else:
                explorer_url = f"https://explorer.celo.org/alfajores/tx/{tx_hash_hex}"
            
            if ctx:
                ctx.info(f"Transaction sent successfully: {tx_hash_hex}")
                await ctx.report_progress(5, 5)
            
            # Clear the session for security
            tx_session.clear_session(session_id)
            
            result = {
                "success": True,
                "transaction_hash": tx_hash_hex,
                "from": address,
                "to": to_address,
                "amount": amount,
                "network": network,
                "explorer_url": explorer_url,
                "message": "Transaction sent successfully. Session has been cleared for security."
            }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            # Make sure to clear session on error too
            tx_session.clear_session(session_id)
            return format_json_response({
                "success": False,
                "error": f"Error sending transaction: {str(e)}"
            })

    @mcp.tool()
    async def send_celo_token(session_id: str, to_address: str, amount: float, token_type: str = "cUSD", network: str = "mainnet", use_alchemy: bool = False, ctx: Context = None) -> str:
        """
        Send Celo stablecoins (cUSD, cEUR) to another address.
        
        Parameters:
        - session_id: Active session ID
        - to_address: Recipient's Celo address
        - amount: Amount of tokens to send
        - token_type: 'cUSD' or 'cEUR'
        - network: 'mainnet' or 'alfajores'
        - use_alchemy: Whether to use Alchemy RPC instead of public RPC
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing {token_type} transfer request")
                await ctx.report_progress(1, 5)
            
            # Get session data
            session_data = tx_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            if not session_data["private_key"]:
                return format_json_response({
                    "success": False,
                    "error": "No private key added to this session. Use add_private_key first."
                })
            
            if token_type not in TOKEN_ADDRESSES:
                return format_json_response({
                    "success": False,
                    "error": f"Unsupported token type: {token_type}. Supported tokens are cUSD, cEUR"
                })
            
            if network not in CELO_NETWORKS:
                return format_json_response({
                    "success": False,
                    "error": f"Unknown network: {network}. Choose 'mainnet' or 'alfajores'"
                })
            
            if ctx:
                ctx.info(f"Connecting to Celo {network}")
                await ctx.report_progress(2, 5)
            
            # Connect to Celo network
            rpc_type = "alchemy" if use_alchemy else "public"
            rpc_url = CELO_NETWORKS[network][rpc_type]
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                return format_json_response({
                    "success": False,
                    "error": f"Failed to connect to Celo {network} at {rpc_url}"
                })
            
            # Load account from private key
            account = Account.from_key(session_data["private_key"])
            address = account.address
            
            # Validate recipient address
            try:
                to_address = Web3.to_checksum_address(to_address)
            except:
                return format_json_response({
                    "success": False,
                    "error": f"Invalid recipient address format: {to_address}"
                })
            
            # Get token contract address
            token_address = TOKEN_ADDRESSES[token_type][network]
            
            if ctx:
                ctx.info(f"Creating token contract instance")
                await ctx.report_progress(3, 5)
            
            # Create contract instance
            token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            # Get token balance
            token_balance = token_contract.functions.balanceOf(address).call()
            token_balance_formatted = token_balance / 10**18  # Assuming 18 decimals for Celo tokens
            
            # Convert amount to token units (with 18 decimals)
            amount_in_token_units = int(amount * 10**18)
            
            # Check if we have enough balance
            if amount_in_token_units > token_balance:
                return format_json_response({
                    "success": False,
                    "error": f"Insufficient balance: {token_balance_formatted} {token_type} available, trying to send {amount} {token_type}"
                })
            
            # Get the current nonce for the account
            nonce = w3.eth.get_transaction_count(address)
            
            # Estimate gas price
            gas_price = w3.eth.gas_price
            
            if ctx:
                ctx.info(f"Building and signing transaction")
                await ctx.report_progress(4, 5)
            
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
            
            # Sign the transaction
            signed_tx = w3.eth.account.sign_transaction(transfer_txn, session_data["private_key"])
            
            # Send the transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            
            # Get the block explorer URL
            if network == "mainnet":
                explorer_url = f"https://explorer.celo.org/mainnet/tx/{tx_hash_hex}"
            else:
                explorer_url = f"https://explorer.celo.org/alfajores/tx/{tx_hash_hex}"
            
            if ctx:
                ctx.info(f"Transaction sent successfully: {tx_hash_hex}")
                await ctx.report_progress(5, 5)
            
            # Clear the session for security
            tx_session.clear_session(session_id)
            
            result = {
                "success": True,
                "transaction_hash": tx_hash_hex,
                "token_type": token_type,
                "from": address,
                "to": to_address,
                "amount": amount,
                "network": network,
                "explorer_url": explorer_url,
                "message": "Transaction sent successfully. Session has been cleared for security."
            }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            # Make sure to clear session on error too
            tx_session.clear_session(session_id)
            return format_json_response({
                "success": False,
                "error": f"Error sending token transaction: {str(e)}"
            })

    @mcp.tool()
    async def sign_message(session_id: str, message: str, ctx: Context = None) -> str:
        """
        Sign a message using the private key in the current session.
        
        Parameters:
        - session_id: Active session ID
        - message: Message to sign
        
        Returns:
        - Signature details
        """
        try:
            from web3 import Web3
            from eth_account import Account
            from eth_account.messages import encode_defunct
            
            if ctx:
                ctx.info(f"Processing message signing request")
                await ctx.report_progress(1, 3)
            
            # Get session data
            session_data = tx_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            if not session_data["private_key"]:
                return format_json_response({
                    "success": False,
                    "error": "No private key added to this session. Use add_private_key first."
                })
            
            if ctx:
                ctx.info(f"Signing message")
                await ctx.report_progress(2, 3)
            
            # Load account from private key
            account = Account.from_key(session_data["private_key"])
            address = account.address
            
            # Sign the message
            encoded_message = encode_defunct(text=message)
            signed_message = account.sign_message(encoded_message)
            
            if ctx:
                ctx.info(f"Message signed successfully")
                await ctx.report_progress(3, 3)
            
            # Don't clear the session after signing a message
            # This allows multiple messages to be signed in one session
            
            w3 = Web3()  # Just for to_hex conversion
            result = {
                "success": True,
                "address": address,
                "message": message,
                "message_hash": w3.to_hex(signed_message.message_hash),
                "signature": w3.to_hex(signed_message.signature),
                "r": str(signed_message.r),
                "s": str(signed_message.s),
                "v": signed_message.v
            }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error signing message: {str(e)}"
            })

    @mcp.tool()
    async def clear_session(session_id: str, ctx: Context = None) -> str:
        """
        Manually clear a transaction session.
        
        Parameters:
        - session_id: Session ID to clear
        
        Returns:
        - Confirmation message
        """
        try:
            if ctx:
                ctx.info(f"Clearing session: {session_id}")
            
            # Check if the session exists
            session_data = tx_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID."
                })
            
            # Clear the session
            tx_session.clear_session(session_id)
            
            result = {
                "success": True,
                "message": "Session cleared successfully."
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error clearing session: {str(e)}"
            })