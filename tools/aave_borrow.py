# tools/aave_borrow.py - Aave borrow and repay operations
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
from tools.aave_session import aave_session, CELO_NETWORKS, AAVE_CONTRACTS, EXPLORER_URL, ERC20_ABI, LENDING_POOL_ABI

def register_aave_borrow_tools(mcp: FastMCP):
    """Register Aave borrow and repay tools with the MCP server."""
    
    @mcp.tool()
    async def borrow_usdc(session_id: str, amount: float, ctx: Context = None) -> str:
        """
        Borrow USDC from Aave.
        Note: Only available on Celo mainnet.
        
        Parameters:
        - session_id: Active Aave session ID
        - amount: Amount of USDC to borrow (e.g., 10.5)
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                ctx.info(f"Processing request to borrow {amount} USDC from Aave")
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
            
            # Convert USDC amount to Wei (USDC has 6 decimals)
            amount_in_wei = int(amount * 10**6)
            
            if ctx:
                ctx.info(f"Borrowing USDC from Aave")
                await ctx.report_progress(3, 3)
            
            # Call the borrow function
            borrow_tx = lending_pool.functions.borrow(
                AAVE_CONTRACTS["USDC_TOKEN"],   # asset address (USDC token)
                amount_in_wei,                 # amount to borrow
                2,                             # interest rate mode (2 = variable)
                0,                             # referral code
                address                        # on behalf of (our own address)
            ).build_transaction({
                'from': address,
                'gas': 400000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the borrow transaction
            signed_borrow_tx = w3.eth.account.sign_transaction(borrow_tx, session_data["private_key"])
            borrow_tx_hash = w3.eth.send_raw_transaction(signed_borrow_tx.raw_transaction)
            borrow_tx_hash_hex = borrow_tx_hash.hex()
            
            # Wait for the borrow transaction to be mined
            borrow_receipt = w3.eth.wait_for_transaction_receipt(borrow_tx_hash)
            
            # Clear the session for security
            aave_session.clear_session(session_id)
            
            if borrow_receipt['status'] == 1:
                result = {
                    "success": True,
                    "message": f"Successfully borrowed {amount} USDC from Aave on Celo mainnet!",
                    "transaction_hash": borrow_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{borrow_tx_hash_hex}",
                    "amount": amount,
                    "session_cleared": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Borrow transaction failed",
                    "transaction_hash": borrow_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{borrow_tx_hash_hex}",
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
                "error": f"Error borrowing USDC from Aave: {str(e)}",
                "session_cleared": True
            })
            
    @mcp.tool()
    async def repay_usdc(session_id: str, amount: float = 0, ctx: Context = None) -> str:
        """
        Repay USDC to Aave.
        Note: Only available on Celo mainnet.
        
        Parameters:
        - session_id: Active Aave session ID
        - amount: Amount of USDC to repay (e.g., 10.5), use 0 to repay all
        
        Returns:
        - Transaction result
        """
        try:
            from web3 import Web3
            from eth_account import Account
            
            if ctx:
                if amount == 0:
                    ctx.info(f"Processing request to repay all USDC to Aave")
                else:
                    ctx.info(f"Processing request to repay {amount} USDC to Aave")
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
            
            # Create contract instances
            lending_pool = w3.eth.contract(address=AAVE_CONTRACTS["LENDING_POOL"], abi=LENDING_POOL_ABI)
            usdc_token = w3.eth.contract(address=AAVE_CONTRACTS["USDC_TOKEN"], abi=ERC20_ABI)
            
            if ctx:
                ctx.info(f"Checking USDC balance")
                await ctx.report_progress(3, 5)
            
            # Convert USDC amount to Wei (USDC has 6 decimals)
            # For repaying all, use uint256 max value
            if amount == 0:
                amount_in_wei = 2**256 - 1  # max uint256 value
            else:
                amount_in_wei = int(amount * 10**6)
            
            # Check USDC balance
            usdc_balance = usdc_token.functions.balanceOf(address).call()
            
            if amount_in_wei != 2**256 - 1 and usdc_balance < amount_in_wei:
                return format_json_response({
                    "success": False,
                    "error": f"Not enough USDC balance. Have {usdc_balance / 10**6} USDC, need {amount} USDC"
                })
            
            if ctx:
                ctx.info(f"Approving USDC for LendingPool")
                await ctx.report_progress(4, 5)
            
            # Approve USDC for lending pool
            approve_tx = usdc_token.functions.approve(
                AAVE_CONTRACTS["LENDING_POOL"],
                amount_in_wei if amount_in_wei != 2**256 - 1 else usdc_balance  # Approve only what we have for max value
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
                # Clear the session for security
                aave_session.clear_session(session_id)
                return format_json_response({
                    "success": False,
                    "error": "USDC approval transaction failed",
                    "transaction_hash": approve_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{approve_tx_hash_hex}",
                    "session_cleared": True
                })
            
            if ctx:
                ctx.info(f"Repaying USDC to Aave")
                await ctx.report_progress(5, 5)
            
            # Call the repay function
            repay_tx = lending_pool.functions.repay(
                AAVE_CONTRACTS["USDC_TOKEN"],   # asset address (USDC token)
                amount_in_wei,                 # amount to repay
                2,                             # interest rate mode (2 = variable)
                address                        # on behalf of (our own address)
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(address),
                'chainId': w3.eth.chain_id
            })
            
            # Sign and send the repay transaction
            signed_repay_tx = w3.eth.account.sign_transaction(repay_tx, session_data["private_key"])
            repay_tx_hash = w3.eth.send_raw_transaction(signed_repay_tx.raw_transaction)
            repay_tx_hash_hex = repay_tx_hash.hex()
            
            # Wait for the repay transaction to be mined
            repay_receipt = w3.eth.wait_for_transaction_receipt(repay_tx_hash)
            
            # Clear the session for security
            aave_session.clear_session(session_id)
            
            if repay_receipt['status'] == 1:
                if amount_in_wei == 2**256 - 1:
                    message = "Successfully repaid all USDC to Aave on Celo mainnet!"
                else:
                    message = f"Successfully repaid {amount} USDC to Aave on Celo mainnet!"
                
                result = {
                    "success": True,
                    "message": message,
                    "transaction_hash": repay_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{repay_tx_hash_hex}",
                    "amount": "all" if amount == 0 else amount,
                    "session_cleared": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Repay transaction failed",
                    "transaction_hash": repay_tx_hash_hex,
                    "explorer_url": f"{EXPLORER_URL}{repay_tx_hash_hex}",
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
                "error": f"Error repaying USDC to Aave: {str(e)}",
                "session_cleared": True
            })