# server.py - Main server entry point
from mcp.server.fastmcp import FastMCP

# Create an MCP server with a name
mcp = FastMCP("Celo Explorer")

# Import and register tools and resources
from resources.greeting import register_greeting_resources
from resources.info import register_info_resources
from resources.dune_info import register_dune_info_resources
from resources.aave_info import register_aave_info_resources
from tools.celo_reader import register_celo_reader_tools
from tools.celo_writer import register_celo_writer_tools
from tools.dune_analytics import register_dune_analytics_tools
from tools.aave_session import register_aave_session_tools
from tools.aave_supply import register_aave_supply_tools
from tools.aave_collateral import register_aave_collateral_tools
from tools.aave_borrow import register_aave_borrow_tools

# Register all tools and resources
register_greeting_resources(mcp)
register_info_resources(mcp)
register_dune_info_resources(mcp)
register_aave_info_resources(mcp)
register_celo_reader_tools(mcp)
register_celo_writer_tools(mcp)
register_dune_analytics_tools(mcp)
register_aave_session_tools(mcp)
register_aave_supply_tools(mcp)
register_aave_collateral_tools(mcp)
register_aave_borrow_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport='stdio')