# resources/info.py - Server information resources
from mcp.server.fastmcp import FastMCP

def register_info_resources(mcp: FastMCP):
    """Register all information resources with the MCP server."""
    
    @mcp.resource("info://server")
    def get_server_info() -> str:
        """Get information about this MCP server"""
        return """
        This is a modular Calculator MCP server.
        It provides:
        - A calculator tool for basic arithmetic
        - An advanced calculator for evaluating expressions
        - A greeting resource that responds with personalized messages
        - This server info resource
        
        Feel free to explore and test the functionality!
        """
