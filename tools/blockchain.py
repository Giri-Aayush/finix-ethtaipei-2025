# tools/blockchain.py - Basic Celo blockchain interactions
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response

def register_blockchain_tools(mcp: FastMCP):
    """Register all blockchain tools with the MCP server."""
    
    @mcp.tool()
    async def get_celo_block_number(ctx: Context = None) -> str:
        """
        Get the current block number on the Celo blockchain.
        
        Returns:
        - The current block number
        """
        try:
            from web3 import Web3
            
            if ctx:
                ctx.info("Connecting to Celo network")
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            
            # Get the latest block number
            block_number = w3.eth.block_number
            
            result = {
                "block_number": block_number,
                "network": "Celo Mainnet"
            }
            
            return format_json_response(result)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error fetching block number: {str(e)}"
    
    @mcp.tool()
    async def get_celo_balance(address: str, ctx: Context = None) -> str:
        """
        Get the CELO balance for a given address.
        
        Parameters:
        - address: The Celo wallet address
        
        Returns:
        - The balance information
        """
        try:
            from web3 import Web3
            
            if ctx:
                ctx.info(f"Connecting to Celo network")
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            
            # Validate address
            if not w3.is_address(address):
                return f"Invalid address format: {address}"
            
            # Get balance in wei
            balance_wei = w3.eth.get_balance(address)
            # Convert to CELO
            balance_celo = w3.from_wei(balance_wei, 'ether')
            
            result = {
                "address": address,
                "balance_wei": str(balance_wei),
                "balance_celo": str(balance_celo),
                "network": "Celo Mainnet"
            }
            
            return format_json_response(result)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error fetching Celo balance: {str(e)}"
    
    @mcp.tool()
    async def get_celo_block_info(block_number: int = None, ctx: Context = None) -> str:
        """
        Get information about a specific block on the Celo blockchain.
        
        Parameters:
        - block_number: The block number to query (default: latest block)
        
        Returns:
        - Block information
        """
        try:
            from web3 import Web3
            
            if ctx:
                ctx.info(f"Connecting to Celo network")
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            
            # Determine which block to query
            if block_number is None:
                block_identifier = 'latest'
                if ctx:
                    ctx.info("Fetching latest block")
            else:
                block_identifier = block_number
                if ctx:
                    ctx.info(f"Fetching block #{block_number}")
            
            # Get block information
            block = w3.eth.get_block(block_identifier)
            
            # Convert block data to a dict, handling non-serializable values
            block_dict = {
                "number": block.number,
                "hash": block.hash.hex(),
                "parentHash": block.parentHash.hex(),
                "timestamp": block.timestamp,
                "miner": block.miner,
                "gasUsed": block.gasUsed,
                "gasLimit": block.gasLimit,
                "transactions": [tx.hex() for tx in block.transactions],
                "transaction_count": len(block.transactions)
            }
            
            return format_json_response(block_dict)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error fetching block info: {str(e)}"
    
    @mcp.tool()
    async def get_celo_transaction(tx_hash: str, ctx: Context = None) -> str:
        """
        Get details of a transaction on the Celo blockchain.
        
        Parameters:
        - tx_hash: The transaction hash
        
        Returns:
        - Transaction details
        """
        try:
            from web3 import Web3
            
            if ctx:
                ctx.info(f"Connecting to Celo network")
            
            # Connect to Celo network
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            
            # Validate transaction hash
            if not tx_hash.startswith('0x') or len(tx_hash) != 66:
                return f"Invalid transaction hash format: {tx_hash}"
            
            if ctx:
                ctx.info(f"Fetching transaction: {tx_hash}")
            
            # Get transaction information
            tx = w3.eth.get_transaction(tx_hash)
            
            if tx is None:
                return f"Transaction not found: {tx_hash}"
            
            # Convert to a serializable dict
            tx_dict = {
                "hash": tx.hash.hex(),
                "from": tx["from"],
                "to": tx.to,
                "value": str(tx.value),
                "value_celo": str(w3.from_wei(tx.value, 'ether')),
                "gas": tx.gas,
                "gasPrice": str(tx.gasPrice),
                "nonce": tx.nonce,
                "blockNumber": tx.blockNumber,
                "blockHash": tx.blockHash.hex() if tx.blockHash else None,
                "transactionIndex": tx.transactionIndex
            }
            
            return format_json_response(tx_dict)
            
        except ImportError:
            return "Web3 library not installed. Please install with: pip3 install web3"
        except Exception as e:
            return f"Error fetching transaction: {str(e)}"
