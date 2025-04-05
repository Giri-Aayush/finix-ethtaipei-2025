# tools/aave_supply.py - Aave supply and withdraw operations
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
from tools.aave_session import aave_session, CELO_NETWORKS, AAVE_CONTRACTS, EXPLORER_URL, ERC20_ABI, LENDING_POOL_ABI

def register_aave_supply_tools(mcp: FastMCP):
    """Register Aave supply and withdraw tools with the MCP server."""
    
    @mcp.tool()
    async def supply_celo(session_id: str, amount: float, ctx: Context = None) -> str:
        """
        Supply CELO to Aave.
        Note: Only available on Celo mainnet.
        
        Parameters:
        - session_id: Active Aave session ID
        - amount: Amount of CELO to supply (e.g., 0.5)
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing Aave supply CELO request")
                await ctx.report_progress(1, 5)
            
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
                await ctx.report_progress(2, 5)
            
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
            
            # Convert CELO amount to wei
            amount_in_wei = w3.to_wei(amount, 'ether')
            
            if ctx:
                ctx.info(f"Checking CELO balance")
                await ctx.report_progress(3, 5)
            
            # Create contract instances
            celo_token = w3.eth.contract(address=AAVE_CONTRACTS["CELO_TOKEN"], abi=ERC20_ABI)
            lending_pool = w3.eth.contract(address=AAVE_CONTRACTS["LENDING_POOL"], abi=LENDING_POOL_ABI)
            
            # Check token balance for the wrapped CELO
            token_balance = celo_token.functions.balanceOf(address).call()
            
            # Check if we have enough wrapped CELO
            if token_balance < amount_in_wei:
                native_balance = w3.eth.get_balance(address)
                return format_json_response({
                    "success": False,
                    "error": f"Not enough wrapped CELO. You have {w3.from_wei(token_balance, 'ether')} wrapped CELO, need {amount} CELO. You need to convert native CELO to wrapped CELO first.",
                    "native_balance": f"{w3.from_wei(native_balance, 'ether')} CELO"
                })
            
            if ctx:
                ctx.info(f"Approving CELO token for Aave LendingPool")
                await ctx.report_progress(4, 5)
            
            # 1. First, approve the CELO token for the lending pool
            approve_tx = celo_token.functions.approve(
                AAVE_CONTRACTS["LENDING_POOL"],
                amount_in_wei
            ).build_transaction({
                'from': address,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the approval transaction
            signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, session_data["private_key"])
            approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
            approve_tx_hash_hex = approve_tx_hash.hex()
            
            # Wait for the approval transaction to be mined
            approve_receipt = w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            
            if approve_receipt['status'] != 1:
                return format_json_response({
                    "success": False,
                    "error": "Approval transaction failed",
                    "tx_hash": approve_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{approve_tx_hash_hex}"
                })
            
            if ctx:
                ctx.info(f"Supplying CELO to Aave")
                await ctx.report_progress(5, 5)
            
            # 2. Now, call the supply function
            supply_tx = lending_pool.functions.supply(
                AAVE_CONTRACTS["CELO_TOKEN"],  # asset address (wrapped CELO token)
                amount_in_wei,                # amount
                address,                      # onBehalfOf (our own address)
                0                             # referralCode
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the supply transaction
            signed_supply_tx = w3.eth.account.sign_transaction(supply_tx, session_data["private_key"])
            supply_tx_hash = w3.eth.send_raw_transaction(signed_supply_tx.raw_transaction)
            supply_tx_hash_hex = supply_tx_hash.hex()
            
            # Wait for the supply transaction to be mined
            supply_receipt = w3.eth.wait_for_transaction_receipt(supply_tx_hash)
            
            # Clear the session for security
            aave_session.clear_session(session_id)
            
            if supply_receipt['status'] == 1:
                result = {
                    "success": True,
                    "message": f"Successfully supplied {amount} CELO to Aave on Celo mainnet! You received aCELO tokens in return, representing your deposit position.",
                    "transaction_hash": supply_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{supply_tx_hash_hex}",
                    "amount": amount,
                    "session_cleared": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Supply transaction failed",
                    "transaction_hash": supply_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{supply_tx_hash_hex}",
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
                "error": f"Error supplying CELO to Aave: {str(e)}",
                "session_cleared": True
            })

    @mcp.tool()
    async def withdraw_celo(session_id: str, amount: float = 0, ctx: Context = None) -> str:
        """
        Withdraw CELO from Aave.
        Note: Only available on Celo mainnet.
        
        Parameters:
        - session_id: Active Aave session ID
        - amount: Amount of CELO to withdraw (e.g., 0.5), use 0 to withdraw all
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing Aave withdraw CELO request")
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
                ctx.info(f"Connecting to Celo mainnet and preparing withdrawal")
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
            
            # For withdrawing all, use uint256 max value
            if amount == 0:
                amount_in_wei = 2**256 - 1  # max uint256 value (withdraw all)
            else:
                amount_in_wei = w3.to_wei(amount, 'ether')
            
            if ctx:
                ctx.info(f"Withdrawing CELO from Aave")
                await ctx.report_progress(3, 3)
            
            # Call the withdraw function
            withdraw_tx = lending_pool.functions.withdraw(
                AAVE_CONTRACTS["CELO_TOKEN"],  # asset address (CELO token)
                amount_in_wei,                # amount to withdraw
                address                       # recipient address (our own address)
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the withdraw transaction
            signed_withdraw_tx = w3.eth.account.sign_transaction(withdraw_tx, session_data["private_key"])
            withdraw_tx_hash = w3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
            withdraw_tx_hash_hex = withdraw_tx_hash.hex()
            
            # Wait for the withdrawal transaction to be mined
            withdraw_receipt = w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
            
            # Clear the session for security
            aave_session.clear_session(session_id)
            
            if withdraw_receipt['status'] == 1:
                if amount == 0:
                    message = "Successfully withdrew all CELO from Aave on Celo mainnet! Your aCELO tokens have been returned in exchange for CELO."
                else:
                    message = f"Successfully withdrew {amount} CELO from Aave on Celo mainnet! Your aCELO tokens have been returned in exchange for CELO."
                
                result = {
                    "success": True,
                    "message": message,
                    "transaction_hash": withdraw_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{withdraw_tx_hash_hex}",
                    "amount": "all" if amount == 0 else amount,
                    "session_cleared": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Withdrawal transaction failed",
                    "transaction_hash": withdraw_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{withdraw_tx_hash_hex}",
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
                "error": f"Error withdrawing CELO from Aave: {str(e)}",
                "session_cleared": True
            })