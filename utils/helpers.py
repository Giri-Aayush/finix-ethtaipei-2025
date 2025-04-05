# utils/helpers.py - Common utility functions
import json
import logging
from typing import Any, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server")

def format_json_response(data: Dict[str, Any], pretty: bool = True) -> str:
    """Format JSON data as a readable string."""
    if pretty:
        return json.dumps(data, indent=2)
    return json.dumps(data)
