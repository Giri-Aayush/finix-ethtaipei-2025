# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server with a name
mcp = FastMCP("Calculator Demo")

# Add a calculator tool
@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform basic arithmetic operations.
    
    Parameters:
    - operation: The operation to perform (add, subtract, multiply, divide)
    - a: First number
    - b: Second number
    
    Returns:
    - The result of the operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Add a more advanced calculator
@mcp.tool()
def advanced_calculate(expression: str) -> float:
    """
    Evaluate a mathematical expression.
    
    Parameters:
    - expression: Mathematical expression as a string (e.g., "2 * (3 + 4)")
    
    Returns:
    - The result of evaluating the expression
    """
    # Note: eval is used for simplicity, but in a production environment,
    # you should use a safer evaluation method
    try:
        # Replace some common mathematical words with symbols
        expression = expression.replace("plus", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("divided by", "/")
        expression = expression.replace("divide", "/")
        expression = expression.replace("multiply", "*")
        expression = expression.replace("subtract", "-")
        expression = expression.replace("add", "+")
        
        result = eval(expression)
        return float(result)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {str(e)}")

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting for the given name"""
    return f"Hello, {name}! Welcome to the Calculator Demo."

# Add a static information resource
@mcp.resource("info://server")
def get_server_info() -> str:
    """Get information about this MCP server"""
    return """
    This is a basic Calculator MCP server.
    It provides:
    - A calculator tool for basic arithmetic
    - An advanced calculator for evaluating expressions
    - A greeting resource that responds with personalized messages
    - This server info resource
    
    Feel free to explore and test the functionality!
    """

if __name__ == "__main__":
    mcp.run(transport='stdio')