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

Read Operations:
1. get_celo_balances
   • Check CELO, cUSD, and cEUR balances for any address
   • Works on both mainnet and Alfajores testnet

2. get_celo_transactions
   • View recent transactions for any Celo address
   • Customize how many blocks to scan and transactions to return

3. get_celo_token_list
   • List all known tokens held by a Celo address
   • Shows token balances with proper decimal formatting

Write Operations (Requires session with private key):
1. create_transaction_session
   • Create a secure session for transactions
   • Session expires after 5 minutes for security

2. add_private_key
   • Add your private key to the session
   • Key is stored only in memory and cleared after use

3. send_celo
   • Send CELO tokens to any address
   • Works on both mainnet and Alfajores

4. send_celo_token
   • Send stablecoins (cUSD, cEUR) to any address
   • Works on both mainnet and Alfajores

5. sign_message
   • Cryptographically sign a message
   • Returns signature that can verify your identity

6. clear_session
   • Manually clear your session when done
   • For security, always clear your session after use

Example Commands:
• "Check the balance for Celo address 0x123..."
• "Show me the last 10 transactions for 0x456... on Alfajores"
• "Create a transaction session for address 0x789..."

Resources:
• greeting://{name} - Get a personalized greeting
• celo://networks - View available Celo networks
• info://server - This server information
• info://celo - General Celo blockchain information
• info://security - Important security information for transactions
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

    @mcp.resource("info://security")
    def get_security_info() -> str:
        """Get security information for Celo transactions"""
        return """
Important Security Information for Celo Transactions

Private Key Security:
• Never share your private key with anyone, not even this service
• When using the transaction tools, your private key is:
  - Only stored temporarily in memory (never on disk)
  - Automatically cleared after 5 minutes or after a transaction
  - Never logged or transmitted outside the server

How Session Security Works:
1. create_transaction_session creates a session linked to your public address
2. add_private_key temporarily stores your key in memory for that session only
3. After a transaction completes, your key is immediately cleared
4. Sessions automatically expire after 5 minutes
5. You can manually clear a session using the clear_session tool

Best Practices:
• Use the Alfajores testnet for testing before mainnet
• Always verify transaction details before confirming
• Clear your session immediately after completing transactions
• For maximum security, use testnet when possible

Warning:
By using the write operations in this MCP server, you acknowledge that you
understand the risks of handling private keys. While we've implemented security
measures, no system is 100% secure. Use these tools at your own risk.
"""