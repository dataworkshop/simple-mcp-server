"""
FastMCP client for testing the Simple Tools Server using HTTP transport.
"""
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    """Main client function to test all available tools."""

    # Connect to the server using Streamable HTTP transport
    server_url = "http://localhost:8000/mcp"

    async with streamablehttp_client(server_url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("=" * 50)
            print("Connected to Simple Tools Server via FastMCP")
            print("=" * 50)
            print()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # Test 1: Generate UUID
            print("Test 1: Generate UUID")
            result = await session.call_tool("generate_uuid", {"version": 4})
            print(f"Result: {result.content[0].text}")
            print()

            # Test 2: Convert temperature
            print("Test 2: Convert temperature (0°C to Fahrenheit)")
            result = await session.call_tool("convert_temperature", {
                "value": 0,
                "from_unit": "C",
                "to_unit": "F"
            })
            print(f"Result: {result.content[0].text}")
            print()

            # Test 3: Text statistics
            print("Test 3: Text statistics")
            test_text = "Hello world!\nThis is a test.\nThree lines total."
            result = await session.call_tool("text_statistics", {"text": test_text})
            print(f"Result: {result.content[0].text}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
