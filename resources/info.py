# resources/info.py - Celo information resources
from mcp.server.fastmcp import FastMCP

def register_info_resources(mcp: FastMCP):
    """Register all information resources with the MCP server."""
    
    @mcp.resource("info://server")
    def get_server_info() -> str:
        """Get information about this MCP server"""
        return """
# Celo Explorer MCP Server

This MCP server provides comprehensive tools for interacting with the Celo blockchain, Aave DeFi protocol, and Dune Analytics.

## 📱 Celo Wallet Tools

* **get_celo_balances**: Check token balances (CELO, cUSD, cEUR) for any address
  Example: "What's the CELO balance for address 0x123..."

* **get_celo_transactions**: View recent transactions for any address
  Example: "Show me the last 5 transactions for 0x456... on Alfajores"

* **get_celo_token_list**: List all tokens held by any address
  Example: "What tokens does 0x789... hold on mainnet?"

## 💸 Transaction Tools

* **create_transaction_session**: Create a secure session for transactions
  Example: "I want to create a transaction session for my address"

* **add_private_key**: Add a private key to your session (stored only in memory)
  Example: "I'd like to add my private key to my session"

* **send_celo**: Send CELO tokens to another address
  Example: "Send 0.1 CELO to 0xabc..."

* **send_celo_token**: Send stablecoins (cUSD, cEUR) to another address
  Example: "Send 5 cUSD to 0xdef..."

* **sign_message**: Sign a message with your private key
  Example: "Sign the message 'Hello, Celo!'"

* **clear_session**: Manually clear your session for security
  Example: "Please clear my transaction session"

## 🏦 Aave DeFi Tools (Mainnet Only)

* **create_aave_session**: Create a secure session for Aave operations
  Example: "Create an Aave session for my address"

* **add_aave_private_key**: Add your private key to Aave session
  Example: "Add my private key to my Aave session"

* **supply_celo**: Supply CELO to Aave to earn interest
  Example: "Supply 1 CELO to Aave"

* **withdraw_celo**: Withdraw your CELO from Aave
  Example: "Withdraw all my CELO from Aave" or "Withdraw 0.5 CELO from Aave"

* **set_celo_collateral**: Enable or disable using CELO as collateral
  Example: "Set my CELO as collateral in Aave"

* **borrow_usdc**: Borrow USDC against your CELO collateral
  Example: "Borrow 10 USDC from Aave"

* **repay_usdc**: Repay your USDC debt to Aave
  Example: "Repay 5 USDC to Aave" or "Repay all my USDC debt"

* **clear_aave_session**: Manually clear your Aave session
  Example: "Clear my Aave session"

## 📊 Dune Analytics Tools

* **get_dune_data**: Fetch data from Dune Analytics queries
  Example: "Show me the first 10 results from Dune query 3196876"

* **search_dune_data**: Search within Dune Analytics data
  Example: "Search for 'ethereum' in Dune query 3196876"

* **get_dune_summary**: Get statistical summary of Dune Analytics data
  Example: "Summarize the data in Dune query 3196876"

* **clear_dune_cache**: Clear cached Dune Analytics data
  Example: "Clear the Dune data cache"

## 📄 Information Resources

* **info://server**: This general information (what you're reading now)
* **info://celo**: General information about the Celo blockchain
* **info://aave**: Information about Aave on Celo
* **info://dune**: Information about Dune Analytics integration
* **aave://workflow**: Step-by-step guide for using Aave
* **aave://risks**: Information about risks when using Aave
* **dune://query_examples**: Example Dune queries for analysis
* **celo://networks**: Information about available Celo networks
* **greeting://{name}**: Get a personalized greeting

## ⚠️ Security Notes

* Private keys are only stored in memory temporarily
* Sessions expire after 5 minutes
* Sessions are cleared after transactions
* Always clear sessions when finished
* All transactions on mainnet use real funds

For more information, visit the GitHub repository: https://github.com/yourusername/celo-explorer-mcp
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

    @mcp.resource("celo://networks")
    def get_celo_networks() -> str:
        """Get information about available Celo networks"""
        return """
Available Celo Networks:

1. Mainnet
   • Production network for real value transactions
   • RPC Endpoint: https://forno.celo.org
   • Explorer: https://explorer.celo.org
   • Features: All protocols including Aave, Ubeswap, Mobius, etc.

2. Alfajores Testnet
   • Test network with free test tokens
   • RPC Endpoint: https://alfajores-forno.celo-testnet.org
   • Explorer: https://alfajores.celoscan.io
   • Faucet: https://celo.org/developers/faucet
   • Note: Aave is NOT available on Alfajores testnet

Network-specific notes:
• Transactions on mainnet use real funds
• Transactions on testnet use test tokens (without real value)
• Some advanced features like Aave are only available on mainnet
• For testing, use Alfajores testnet when possible
"""