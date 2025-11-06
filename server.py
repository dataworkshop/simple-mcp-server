import uuid
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Simple Tools Server")


@mcp.tool()
def generate_uuid(version: int = 4) -> str:
    """
    Generate a random UUID.

    Args:
        version: UUID version (default 4)

    Returns:
        String containing the generated UUID
    """
    return str(uuid.uuid4()) if version == 4 else str(uuid.uuid1())


@mcp.tool()
def convert_temperature(value: float, from_unit: str = "C", to_unit: str = "F") -> float:
    """
    Convert temperature between Celsius and Fahrenheit.

    Args:
        value: Temperature value to convert
        from_unit: Source unit ('C' or 'F')
        to_unit: Target unit ('C' or 'F')

    Returns:
        Converted temperature value
    """
    if from_unit == "C" and to_unit == "F":
        return (value * 9/5) + 32
    elif from_unit == "F" and to_unit == "C":
        return (value - 32) * 5/9
    return value


@mcp.tool()
def text_statistics(text: str) -> dict:
    """
    Calculate basic text statistics.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with statistics (character count, word count, line count)
    """
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines())
    }


if __name__ == "__main__":
    # Run with Streamable HTTP transport (recommended for production)
    mcp.run(transport="http")
