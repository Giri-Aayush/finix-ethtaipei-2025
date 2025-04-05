# utils/helpers.py - Helper functions for Celo MCP Server
import json
import logging
from typing import Any, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_debug.log',
    filemode='a'
)
logger = logging.getLogger("celo_explorer")

def format_json_response(data: Dict[str, Any], pretty: bool = True) -> str:
    """Format JSON data as a readable string."""
    if pretty:
        return json.dumps(data, indent=2)
    return json.dumps(data)

def format_address(address: str) -> str:
    """Format a blockchain address with ellipsis if too long."""
    if not address:
        return "Unknown"
    if len(address) > 42:  # Standard Ethereum/Celo address length is 42 chars (with 0x)
        return address[:10] + '...' + address[-8:]
    return address

def format_celo_amount(amount: float, symbol: str = "CELO") -> str:
    """Format a CELO amount with appropriate precision."""
    if amount > 1:
        return f"{amount:.4f} {symbol}"
    else:
        return f"{amount:.6f} {symbol}"