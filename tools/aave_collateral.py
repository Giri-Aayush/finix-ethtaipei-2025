# tools/aave_collateral.py - Aave collateral management operations
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
from tools.aave_session import aave_session, CELO_NETWORKS, AAVE_CONTRACTS, EXPLORER_URL, LENDING_POOL_ABI

def register_aave_collateral_tools(mcp: FastMCP):
    """Register Aave collateral management tools with the MCP server."""
    
    @mcp.tool()
    async def set_celo_collateral(session_id: str, use_as_collateral: bool = True, ctx: Context = None) -> str:
        """
        Set CELO as collateral or not in Aave.
        Note: Only available on Celo mainnet.
        
        Parameters:
        - session_id: Active Aave session ID
        - use_as_collateral: Whether to use CELO as collateral (True) or not (False)
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing request to set CELO collateral status to: {use_as_collateral}")
                await ctx.report_progress(1, 3)
            
            # Get session data
            session_data = aave_session.get_session_data(session_id)
            if not session_data:
                return format_json_response({
                    "success": False,
                    "error": "Invalid or expired session ID. Please create a new session."
                })
            
            if not session_data["private_key"]:
                return format_json_response({
                    "success": False,
                    "error": "No private key added to this session. Use add_aave_private_key first."
                })
            
            if ctx:
                ctx.info(f"Connecting to Celo mainnet")
                await ctx.report_progress(2, 3)
            
            # Connect to Celo mainnet - Aave is only available on mainnet
            rpc_url = CELO_NETWORKS["mainnet"]["alchemy"]
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                return format_json_response({
                    "success": False,
                    "error": f"Failed to connect to Celo mainnet at {rpc_url}"
                })
            
            # Load account from private key
            account = Account.from_key(session_data["private_key"])
            address = account.address
            
            # Create lending pool contract instance
            lending_pool = w3.eth.contract(address=AAVE_CONTRACTS["LENDING_POOL"], abi=LENDING_POOL_ABI)
            
            if ctx:
                ctx.info(f"Setting CELO collateral status")
                await ctx.report_progress(3, 3)
            
            # Call the setUserUseReserveAsCollateral function
            set_collateral_tx = lending_pool.functions.setUserUseReserveAsCollateral(
                AAVE_CONTRACTS["CELO_TOKEN"],  # asset address (CELO token)
                use_as_collateral           # whether to use as collateral or not
            ).build_transaction({
                'from': address,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the set collateral transaction
            signed_set_collateral_tx = w3.eth.account.sign_transaction(set_collateral_tx, session_data["private_key"])
            set_collateral_tx_hash = w3.eth.send_raw_transaction(signed_set_collateral_tx.raw_transaction)
            set_collateral_tx_hash_hex = set_collateral_tx_hash.hex()
            
            # Wait for the set collateral transaction to be mined
            set_collateral_receipt = w3.eth.wait_for_transaction_receipt(set_collateral_tx_hash)
            
            # Clear the session for security
            aave_session.clear_session(session_id)
            
            if set_collateral_receipt['status'] == 1:
                if use_as_collateral:
                    message = "Successfully set CELO to be used as collateral in Aave!"
                else:
                    message = "Successfully set CELO to NOT be used as collateral in Aave!"
                
                result = {
                    "success": True,
                    "message": message,
                    "use_as_collateral": use_as_collateral,
                    "transaction_hash": set_collateral_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{set_collateral_tx_hash_hex}",
                    "session_cleared": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Set collateral transaction failed",
                    "transaction_hash": set_collateral_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{set_collateral_tx_hash_hex}",
                    "session_cleared": True
                }
            
            return format_json_response(result)
        
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            # Make sure to clear session on error too
            aave_session.clear_session(session_id)
            return format_json_response({
                "success": False,
                "error": f"Error setting CELO collateral status: {str(e)}",
                "session_cleared": True
            })