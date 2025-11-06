"""
Pure httpx client for testing the Simple Tools Server.
Makes direct HTTP requests using JSON-RPC protocol.
"""
import httpx
import json
import re


class MCPClient:
    """Simple MCP client using only httpx for HTTP requests."""

    def __init__(self, base_url: str = "http://localhost:8000/mcp"):
        self.base_url = base_url
        self.session_id = None
        self.request_id = 0

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    def _build_request(self, method: str, params: dict = None) -> dict:
        """Build JSON-RPC request."""
        return {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }

    def _get_headers(self) -> dict:
        """Get request headers including session ID if available."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    def _parse_sse_response(self, text: str) -> dict:
        """Parse Server-Sent Events response and extract JSON data."""
        # SSE format: "event: message\ndata: {...}\n\n"
        match = re.search(r'data: (.+)', text)
        if match:
            return json.loads(match.group(1))
        # Fallback: try parsing as plain JSON
        return json.loads(text)

    def initialize(self) -> dict:
        """Initialize MCP session."""
        request = self._build_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "httpx-client",
                "version": "1.0.0"
            }
        })

        response = httpx.post(
            self.base_url,
            json=request,
            headers=self._get_headers()
        )

        # Check for session ID in response headers
        if "Mcp-Session-Id" in response.headers:
            self.session_id = response.headers["Mcp-Session-Id"]

        return self._parse_sse_response(response.text)

    def list_tools(self) -> dict:
        """List available tools."""
        request = self._build_request("tools/list")

        response = httpx.post(
            self.base_url,
            json=request,
            headers=self._get_headers()
        )

        return self._parse_sse_response(response.text)

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a specific tool."""
        request = self._build_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        response = httpx.post(
            self.base_url,
            json=request,
            headers=self._get_headers()
        )

        return self._parse_sse_response(response.text)


def main():
    """Main function to test all tools."""
    client = MCPClient()

    print("=" * 50)
    print("Connected to Simple Tools Server via httpx")
    print("=" * 50)
    print()

    # Initialize session
    print("Initializing session...")
    init_response = client.initialize()
    print(f"Server info: {init_response['result']['serverInfo']}")
    print()

    # List available tools
    print("Available tools:")
    tools_response = client.list_tools()
    for tool in tools_response["result"]["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")
    print()

    # Test 1: Generate UUID
    print("Test 1: Generate UUID")
    result = client.call_tool("generate_uuid", {"version": 4})
    print(f"Result: {result['result']['content'][0]['text']}")
    print()

    # Test 2: Convert temperature
    print("Test 2: Convert temperature (0°C to Fahrenheit)")
    result = client.call_tool("convert_temperature", {
        "value": 0,
        "from_unit": "C",
        "to_unit": "F"
    })
    print(f"Result: {result['result']['content'][0]['text']}")
    print()

    # Test 3: Text statistics
    print("Test 3: Text statistics")
    test_text = "Hello world!\nThis is a test.\nThree lines total."
    result = client.call_tool("text_statistics", {"text": test_text})
    print(f"Result: {result['result']['content'][0]['text']}")
    print()


if __name__ == "__main__":
    main()
