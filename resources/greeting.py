# resources/greeting.py - Greeting resources
from mcp.server.fastmcp import FastMCP

def register_greeting_resources(mcp: FastMCP):
    """Register all greeting resources with the MCP server."""
    
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting for the given name"""
        return f"Hello, {name}! Welcome to the Calculator Demo."
