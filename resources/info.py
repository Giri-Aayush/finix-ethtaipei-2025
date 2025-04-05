# resources/info.py - Celo information resources
from mcp.server.fastmcp import FastMCP

def register_info_resources(mcp: FastMCP):
    """Register all information resources with the MCP server."""
    
    @mcp.resource("info://server")
    def get_server_info() -> str:
        """Get information about this MCP server"""
        return """
Welcome to the Celo Explorer MCP Server!

This server helps you interact with the Celo blockchain directly through Claude.

Available Tools:

1. get_celo_balances
   • Check CELO, cUSD, and cEUR balances for any address
   • Works on both mainnet and Alfajores testnet

2. get_celo_transactions
   • View recent transactions for any Celo address
   • Customize how many blocks to scan and transactions to return

3. get_celo_token_list
   • List all known tokens held by a Celo address
   • Shows token balances with proper decimal formatting

Example Commands:
• "Check the balance for Celo address 0x123..."
• "Show me the last 10 transactions for 0x456... on Alfajores"
• "What tokens does 0x789... hold on mainnet?"

Resources:
• greeting://{name} - Get a personalized greeting
• celo://networks - View available Celo networks
• info://server - This server information
"""
    
    @mcp.resource("info://celo")
    def get_celo_info() -> str:
        """Get information about Celo blockchain"""
        return """
About Celo Blockchain:

Celo is a carbon-negative, EVM-compatible blockchain designed for mobile-first financial applications. It features:

• A proof-of-stake consensus mechanism
• Native stablecoins including cUSD, cEUR, and cREAL
• Fast transaction finality (5 seconds)
• Low transaction fees
• Built-in address-based encryption
• Phone number verification system

Key Celo Token Information:
• CELO: Native token used for fees, governance, and staking
• cUSD: Stablecoin pegged to the US Dollar
• cEUR: Stablecoin pegged to the Euro
• cREAL: Stablecoin pegged to the Brazilian Real

Useful Links:
• Official Website: https://celo.org
• Developer Documentation: https://docs.celo.org
• GitHub: https://github.com/celo-org
• Block Explorer: https://explorer.celo.org
"""