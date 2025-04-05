# server.py - Main server entry point
from mcp.server.fastmcp import FastMCP

# Create an MCP server with a name
mcp = FastMCP("Celo Calculator")

# Import and register tools and resources
from tools.calculator import register_calculator_tools
from resources.greeting import register_greeting_resources
from resources.info import register_info_resources
from tools.blockchain import register_blockchain_tools

# Register all tools and resources
register_calculator_tools(mcp)
register_greeting_resources(mcp)
register_info_resources(mcp)
register_blockchain_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport='stdio')