# tools/calculator.py - Calculator tools
from mcp.server.fastmcp import FastMCP

def register_calculator_tools(mcp: FastMCP):
    """Register all calculator tools with the MCP server."""
    
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
    
    @mcp.tool()
    def advanced_calculate(expression: str) -> float:
        """
        Evaluate a mathematical expression.
        
        Parameters:
        - expression: Mathematical expression as a string (e.g., "2 * (3 + 4)")
        
        Returns:
        - The result of evaluating the expression
        """
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
