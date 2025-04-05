# tools/aave_session.py - Aave session management
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
import time
from typing import Dict, Optional

# Celo network RPC endpoints
CELO_NETWORKS = {
    "mainnet": {
        "public": "https://forno.celo.org",
        "alchemy": "https://celo-mainnet.g.alchemy.com/v2/IJbweBVOnwnTeoaIg10-jGVFe8aPfaH5"
    }
}

# Contract addresses - Aave only available on mainnet
AAVE_CONTRACTS = {
    "LENDING_POOL": "0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402",  # Aave lending pool
    "CELO_TOKEN": "0x471EcE3750Da237f93B8E339c536989b8978a438",    # CELO token address
    "USDC_TOKEN": "0xcebA9300f2b948710d2653dD7B07f33A8B32118C",    # USDC token address
}

# Explorer URL for transaction tracking
EXPLORER_URL = "https://celoscan.io/tx/0x"

# ABI for ERC20 tokens
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

# Secure session management for temporary private key storage
class AaveTransactionSession:
    """Manages a secure, time-limited transaction session for Aave operations"""
    
    def __init__(self, timeout_seconds: int = 300):
        self.sessions: Dict[str, Dict] = {}
        self.timeout_seconds = timeout_seconds
    
    def create_session(self, public_address: str) -> str:
        """Create a new session for a public address, returns session ID"""
        import hashlib
        session_id = f"aave_{int(time.time())}_{hashlib.sha256(public_address.encode()).hexdigest()[:8]}"
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
aave_session = AaveTransactionSession(timeout_seconds=300)  # 5-minute timeout

def register_aave_session_tools(mcp: FastMCP):
    """Register Aave session management tools with the MCP server."""
    
    @mcp.tool()
    async def create_aave_session(address: str, ctx: Context = None) -> str:
        """
        Create a new session for Aave operations.
        
        Parameters:
        - address: Celo address to create session for
        
        Returns:
        - Session ID to use for future Aave operations
        """
        try:
            from web3 import Web3
            
            # Validate address
            try:
                address = Web3.to_checksum_address(address)
            except:
                return format_json_response({
                    "success": False,
                    "error": f"Invalid address format: {address}"
                })
            
            if ctx:
                ctx.info(f"Creating Aave session for address: {address}")
            
            # Create a new session
            session_id = aave_session.create_session(address)
            
            result = {
                "success": True,
                "session_id": session_id,
                "public_address": address,
                "expires_in_seconds": 300,
                "message": "Aave session created. Use this session_id with add_private_key to enable Aave operations."
            }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error creating Aave session: {str(e)}"
            })

    @mcp.tool()
    async def add_aave_private_key(session_id: str, private_key: str, ctx: Context = None) -> str:
        """
        Add a private key to an existing Aave session.
        SECURITY WARNING: Private keys provide full access to funds. This tool should only be used
        in secure environments. The private key will be held in memory temporarily.
        
        Parameters:
        - session_id: Session ID from create_aave_session
        - private_key: Private key for the address (with or without 0x prefix)
        
        Returns:
        - Confirmation message
        """
        try:
            if ctx:
                ctx.info(f"Adding private key to Aave session: {session_id}")
            
            # Ensure private key has 0x prefix
            if not private_key.startswith("0x"):
                private_key = f"0x{private_key}"
            
            # Add the private key to the session
            if not aave_session.add_private_key(session_id, private_key):
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            result = {
                "success": True,
                "message": "Private key added to Aave session. You can now perform Aave operations until the session expires.",
                "warning": "Your private key is stored in memory and will be automatically cleared after 5 minutes."
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error adding private key: {str(e)}"
            })

    @mcp.tool()
    async def clear_aave_session(session_id: str, ctx: Context = None) -> str:
        """
        Manually clear an Aave transaction session.
        
        Parameters:
        - session_id: Session ID to clear
        
        Returns:
        - Confirmation message
        """
        try:
            if ctx:
                ctx.info(f"Clearing Aave session: {session_id}")
            
            # Check if the session exists
            session_data = aave_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID."
                })
            
            # Clear the session
            aave_session.clear_session(session_id)
            
            result = {
                "success": True,
                "message": "Aave session cleared successfully."
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "success": False,
                "error": f"Error clearing Aave session: {str(e)}"
            })