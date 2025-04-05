# resources/dune_info.py - Dune Analytics information resources
from mcp.server.fastmcp import FastMCP

def register_dune_info_resources(mcp: FastMCP):
    """Register all Dune Analytics information resources with the MCP server."""
    
    @mcp.resource("info://dune")
    def get_dune_info() -> str:
        """Get information about Dune Analytics integration"""
        return """
About Dune Analytics Integration:

This MCP server integrates with Dune Analytics to provide on-chain data analysis capabilities.
Dune Analytics is a powerful platform that allows querying blockchain data using SQL.

Available Dune Tools:

1. get_dune_data
   - Fetches data from a specific Dune query
   - Returns data in a paginated format (10 results by default)
   - Example: "Show me the first 10 results from Dune query 3196876"

2. search_dune_data
   - Allows searching within Dune query results
   - Can search in specific columns or across all columns
   - Example: "Search for 'ethereum' in Dune query results"

3. get_dune_summary
   - Provides statistical summary of Dune query data
   - Shows column types, null counts, ranges, and common values
   - Example: "Give me a summary of the data in Dune query 3196876"

4. clear_dune_cache
   - Clears cached Dune data to fetch fresh results
   - Example: "Clear the Dune data cache"

Default Query:
The default query (ID: 3196876) provides Celo blockchain metrics and statistics.
You can specify a different query ID if you have other Dune queries you want to analyze.

Usage Tips:
- Results are paginated by default (10 per page)
- You can request specific pages: "Show me page 2 of Dune query results"
- Data is cached for performance - use clear_dune_cache for fresh data
- Each query includes a link to view it on Dune's website
"""
    
    @mcp.resource("dune://query_examples")
    def get_dune_query_examples() -> str:
        """Get example Dune queries to analyze with this MCP server"""
        return """
Example Dune Queries for Celo Blockchain Analysis:

1. Celo Blockchain Metrics (Query ID: 3196876)
   - Overview of Celo blockchain statistics
   - Includes transaction counts, active addresses, volumes, etc.

2. Celo DeFi Protocol Stats (Query ID: 3196877) 
   - Data on Celo DeFi protocols like Mento, Ubeswap
   - TVL, volumes, and usage metrics

3. Celo Stablecoin Analysis (Query ID: 3196878)
   - Statistics on cUSD, cEUR, and cREAL usage
   - Transfer volumes, active addresses, etc.

4. Celo NFT Market Overview (Query ID: 3196879)
   - NFT sales, collections, and marketplace activity
   - Top collections, sales volumes, etc.

Note: These are example query IDs - replace with actual Dune query IDs for your analysis.
Make sure you have permission to access these queries through the Dune API.

The Dune API requires an API key stored in the DUNE_API_KEY environment variable.
"""