# resources/info.py - Server information resources
from mcp.server.fastmcp import FastMCP

def register_info_resources(mcp: FastMCP):
    """Register all information resources with the MCP server."""
    
    @mcp.resource("info://server")
    def get_server_info() -> str:
        """Get information about this MCP server"""
        return """
        This is a Celo Explorer MCP server.
        
        It provides:
        
        Calculator Tools:
        - Basic calculator for arithmetic operations
        - Advanced calculator for evaluating expressions
        
        Celo Blockchain Tools:
        - Check token balances (CELO, cUSD, cEUR) for any address
        - View recent transactions for any address
        - List all tokens held by an address
        
        Resources:
        - Greeting resource that responds with personalized messages
        - This server info resource
        
        Usage Examples:
        - "Check the CELO balance for address 0x123..."
        - "Show me the recent transactions for 0x456..."
        - "List all tokens held by 0x789..."
        """