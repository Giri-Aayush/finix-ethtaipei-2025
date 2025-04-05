# resources/greeting.py - Celo-focused greeting resources
from mcp.server.fastmcp import FastMCP

def register_greeting_resources(mcp: FastMCP):
    """Register all greeting resources with the MCP server."""
    
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting for the given name"""
        return f"""
Hello {name}! Welcome to the Celo Explorer.

I'm here to help you explore the Celo blockchain. You can:
• Check token balances for any Celo address
• View recent transactions for any address
• Get a list of tokens held by an address

You can use these tools on both Celo mainnet and the Alfajores testnet.

Try asking me to "check the CELO balance for address 0x..." or "show me recent transactions for 0x..."
"""
    
    @mcp.resource("celo://networks")
    def get_available_networks() -> str:
        """Get information about available Celo networks"""
        return """
Available Celo Networks:

1. Mainnet
   • Production network for real value transactions
   • RPC Endpoint: https://forno.celo.org
   • Explorer: https://explorer.celo.org

2. Alfajores Testnet
   • Test network with free test tokens
   • RPC Endpoint: https://alfajores-forno.celo-testnet.org
   • Explorer: https://alfajores.celoscan.io
   • Faucet: https://celo.org/developers/faucet

You can specify which network to use when checking balances or transactions.
"""