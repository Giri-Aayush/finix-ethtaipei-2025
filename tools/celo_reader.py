# tools/celo_reader.py - Celo blockchain read operations
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
from datetime import datetime
import json

# Contract ABI for ERC-20 tokens
ERC20_ABI = json.loads('''[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
]''')

# Network configurations
NETWORKS = {
    "mainnet": {
        "rpc_url": "https://forno.celo.org",
        "block_explorer": "https://explorer.celo.org",
        "contracts": {
            "CELO": "0x471EcE3750Da237f93B8E339c536989b8978a438",
            "CUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
            "CEUR": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73"
        }
    },
    "alfajores": {
        "rpc_url": "https://alfajores-forno.celo-testnet.org",
        "block_explorer": "https://alfajores.celoscan.io",
        "contracts": {
            "CELO": "0xF194afDf50B03e69Bd7D057c1Aa9e10c9954E4C9",
            "CUSD": "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1",
            "CEUR": "0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F"
        }
    }
}

def register_celo_reader_tools(mcp: FastMCP):
    """Register all Celo read operation tools with the MCP server."""
    
    @mcp.tool()
    async def get_celo_balances(address: str, network: str = "mainnet", ctx: Context = None) -> str:
        """
        Get token balances (CELO, cUSD, cEUR) for a Celo address.
        
        Parameters:
        - address: The Celo wallet address
        - network: 'mainnet' or 'alfajores' (testnet)
        
        Returns:
        - Token balances information
        """
        try:
            from web3 import Web3
            
            if network.lower() not in NETWORKS:
                return f"Invalid network: {network}. Choose 'mainnet' or 'alfajores'."
            
            network_config = NETWORKS[network.lower()]
            
            if ctx:
                ctx.info(f"Connecting to Celo {network}")
                await ctx.report_progress(1, 4)
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
            
            # Validate address
            try:
                address = Web3.to_checksum_address(address)
            except:
                return f"Invalid address format: {address}"
            
            if ctx:
                ctx.info(f"Fetching CELO balance")
                await ctx.report_progress(2, 4)
            
            # Get native CELO balance
            result = {}
            try:
                celo_balance = w3.eth.get_balance(address)
                result["CELO"] = float(w3.from_wei(celo_balance, "ether"))
            except Exception as e:
                result["CELO_error"] = str(e)
            
            if ctx:
                ctx.info(f"Fetching stablecoin balances")
                await ctx.report_progress(3, 4)
            
            # Get cUSD balance
            try:
                cusd_contract = w3.eth.contract(
                    address=Web3.to_checksum_address(network_config["contracts"]["CUSD"]),
                    abi=ERC20_ABI
                )
                cusd_balance = cusd_contract.functions.balanceOf(address).call()
                cusd_decimals = cusd_contract.functions.decimals().call()
                result["cUSD"] = float(cusd_balance) / 10**cusd_decimals
            except Exception as e:
                result["cUSD_error"] = str(e)
            
            # Get cEUR balance
            try:
                ceur_contract = w3.eth.contract(
                    address=Web3.to_checksum_address(network_config["contracts"]["CEUR"]),
                    abi=ERC20_ABI
                )
                ceur_balance = ceur_contract.functions.balanceOf(address).call()
                ceur_decimals = ceur_contract.functions.decimals().call()
                result["cEUR"] = float(ceur_balance) / 10**ceur_decimals
            except Exception as e:
                result["cEUR_error"] = str(e)
            
            if ctx:
                await ctx.report_progress(4, 4)
            
            # Add additional information
            result["address"] = address
            result["network"] = network
            result["block_explorer_url"] = f"{network_config['block_explorer']}/address/{address}"
            
            return format_json_response(result)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error checking balances: {str(e)}"
    
    @mcp.tool()
    async def get_celo_transactions(address: str, blocks_to_scan: int = 100, max_count: int = 10, network: str = "mainnet", ctx: Context = None) -> str:
        """
        Get recent transactions for a Celo address.
        
        Parameters:
        - address: The Celo wallet address
        - blocks_to_scan: Number of recent blocks to scan (default: 100)
        - max_count: Maximum number of transactions to return (default: 10)
        - network: 'mainnet' or 'alfajores' (testnet)
        
        Returns:
        - Recent transactions list
        """
        try:
            from web3 import Web3
            
            if network.lower() not in NETWORKS:
                return f"Invalid network: {network}. Choose 'mainnet' or 'alfajores'."
            
            if blocks_to_scan < 1 or blocks_to_scan > 1000:
                return "blocks_to_scan must be between 1 and 1000"
            
            if max_count < 1 or max_count > 50:
                return "max_count must be between 1 and 50"
            
            network_config = NETWORKS[network.lower()]
            
            if ctx:
                ctx.info(f"Connecting to Celo {network}")
                await ctx.report_progress(1, 3)
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
            
            # Validate address
            try:
                address = Web3.to_checksum_address(address)
            except:
                return f"Invalid address format: {address}"
            
            # Get most recent block number
            try:
                latest_block = w3.eth.block_number
                
                if ctx:
                    ctx.info(f"Scanning the last {blocks_to_scan} blocks for transactions (current block: {latest_block})")
                    await ctx.report_progress(2, 3)
                
                # Limit blocks to scan to what was requested
                scan_blocks = min(blocks_to_scan, latest_block)
                
                transactions = []
                tx_count = 0
                
                # Loop through recent blocks
                for block_num in range(latest_block, latest_block - scan_blocks, -1):
                    if tx_count >= max_count:
                        break
                    
                    try:
                        block = w3.eth.get_block(block_num, full_transactions=True)
                        
                        for tx in block['transactions']:
                            # Check if the transaction involves our address
                            if (tx.get('from', '').lower() == address.lower() or 
                                tx.get('to', '').lower() == address.lower()):
                                
                                tx_count += 1
                                
                                # Get transaction status
                                try:
                                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                                    tx_status = "Success" if receipt.get('status') == 1 else "Failed"
                                    gas_used = receipt.get('gasUsed', 0)
                                except:
                                    tx_status = "Unknown"
                                    gas_used = None
                                
                                # Format transaction data
                                tx_data = {
                                    "hash": tx['hash'].hex(),
                                    "block_number": tx['blockNumber'],
                                    "from": tx.get('from', 'Unknown'),
                                    "to": tx.get('to', 'Contract Creation'),
                                    "value": float(w3.from_wei(tx.get('value', 0), "ether")),
                                    "timestamp": datetime.fromtimestamp(block['timestamp']).isoformat(),
                                    "gas_used": gas_used,
                                    "status": tx_status,
                                    "tx_explorer_url": f"{network_config['block_explorer']}/tx/{tx['hash'].hex()}"
                                }
                                
                                transactions.append(tx_data)
                                
                                if tx_count >= max_count:
                                    break
                    except Exception as e:
                        if ctx:
                            ctx.info(f"Error processing block {block_num}: {e}")
                        continue
                
                if ctx:
                    await ctx.report_progress(3, 3)
                
                # Prepare result
                result = {
                    "address": address,
                    "network": network,
                    "latest_block": latest_block,
                    "blocks_scanned": scan_blocks,
                    "transactions_found": len(transactions),
                    "transactions": transactions,
                    "block_explorer_url": f"{network_config['block_explorer']}/address/{address}"
                }
                
                return format_json_response(result)
                
            except Exception as e:
                return f"Error scanning blocks: {str(e)}"
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error getting transaction history: {str(e)}"
    
    @mcp.tool()
    async def get_celo_token_list(address: str, network: str = "mainnet", ctx: Context = None) -> str:
        """
        List all known tokens held by a Celo address.
        
        Parameters:
        - address: The Celo wallet address
        - network: 'mainnet' or 'alfajores' (testnet)
        
        Returns:
        - List of tokens and balances
        """
        try:
            from web3 import Web3
            
            if network.lower() not in NETWORKS:
                return f"Invalid network: {network}. Choose 'mainnet' or 'alfajores'."
            
            network_config = NETWORKS[network.lower()]
            
            if ctx:
                ctx.info(f"Connecting to Celo {network}")
                await ctx.report_progress(1, 2)
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
            
            # Validate address
            try:
                address = Web3.to_checksum_address(address)
            except:
                return f"Invalid address format: {address}"
            
            tokens = []
            
            # Define tokens to check based on network
            token_list = [
                {"address": network_config["contracts"]["CELO"], "name": "Celo", "symbol": "CELO", "decimals": 18},
                {"address": network_config["contracts"]["CUSD"], "name": "Celo Dollar", "symbol": "cUSD", "decimals": 18},
                {"address": network_config["contracts"]["CEUR"], "name": "Celo Euro", "symbol": "cEUR", "decimals": 18}
            ]
            
            # Add alfajores-specific tokens
            if network.lower() == "alfajores":
                token_list.extend([
                    {"address": "0xE4D517785D091D3c54818832dB6094bcc2744545", "name": "Celo Brazilian Real", "symbol": "cREAL", "decimals": 18},
                    {"address": "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B", "name": "USD Coin", "symbol": "USDC", "decimals": 18}
                ])
            
            if ctx:
                ctx.info(f"Checking balances for {len(token_list)} tokens")
                await ctx.report_progress(2, 2)
            
            # Get balances for each token
            for token_info in token_list:
                try:
                    token_contract = w3.eth.contract(
                        address=Web3.to_checksum_address(token_info["address"]),
                        abi=ERC20_ABI
                    )
                    
                    # Get balance
                    balance = token_contract.functions.balanceOf(address).call()
                    # Convert to token units
                    balance_formatted = float(balance) / 10**token_info["decimals"]
                    
                    tokens.append({
                        "name": token_info["name"],
                        "symbol": token_info["symbol"],
                        "address": token_info["address"],
                        "balance": balance_formatted,
                        "balance_raw": str(balance),
                        "decimals": token_info["decimals"]
                    })
                except Exception as e:
                    tokens.append({
                        "name": token_info["name"],
                        "symbol": token_info["symbol"],
                        "address": token_info["address"],
                        "error": str(e)
                    })
            
            # Prepare result
            result = {
                "address": address,
                "network": network,
                "token_count": len(tokens),
                "tokens": tokens,
                "block_explorer_url": f"{network_config['block_explorer']}/address/{address}"
            }
            
            return format_json_response(result)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error getting token list: {str(e)}"