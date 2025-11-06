# Simple MCP Server

A simple Model Context Protocol (MCP) server built with FastMCP, featuring three utility tools.

## Tools

1. **generate_uuid** - Generates a random UUID (version 4 or 1)
2. **convert_temperature** - Converts temperature between Celsius and Fahrenheit
3. **text_statistics** - Calculates basic text statistics (characters, words, lines)

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Usage

### Running the Server

Start the MCP server with HTTP transport:

```bash
uv run server.py
```

The server will start on `http://localhost:8000/mcp` by default.

### Testing with FastMCP Client

Run the FastMCP-based client:

```bash
uv run client_fastmcp.py
```

### Testing with httpx Client

Run the pure httpx client (no MCP libraries required):

```bash
uv run client_httpx.py
```

### Testing with curl Client

Run the bash script using only curl and jq:

```bash
./client_curl.sh
```

**Requirements for curl client:**
- `curl` (for HTTP requests)
- `jq` (for JSON parsing)
- Standard Unix tools (`grep`, `sed`, `awk`, `tr`)

## Project Structure

- `server.py` - MCP server with three utility tools
- `client_fastmcp.py` - Client using FastMCP library
- `client_httpx.py` - Client using only httpx for direct HTTP requests
- `client_curl.sh` - Bash script client using curl and jq
- `main.py` - Original template file (not used)

## Example Output

All three clients will:
1. Connect to the server
2. List available tools
3. Test generate_uuid (generates a UUID v4)
4. Test convert_temperature (converts 0°C to Fahrenheit → 32.0°F)
5. Test text_statistics (counts characters, words, and lines in sample text)

Example:
```
Test 1: Generate UUID
Result: 98f99e94-7357-4dd4-85eb-76819fad3ada

Test 2: Convert temperature (0°C to Fahrenheit)
Result: 32.0

Test 3: Text statistics
Result: {"characters":47,"words":9,"lines":3}
```

## Technical Details

- **Transport**: Streamable HTTP (MCP protocol over HTTP)
- **Endpoint**: `/mcp`
- **Response Format**: Server-Sent Events (SSE)
- **Session Management**: Server assigns session ID via `Mcp-Session-Id` header

### Client Implementations

1. **FastMCP Client** (`client_fastmcp.py`):
   - Uses official MCP Python SDK
   - Handles SSE automatically
   - Full protocol support

2. **httpx Client** (`client_httpx.py`):
   - Pure Python with only httpx dependency
   - Manual JSON-RPC implementation
   - Custom SSE parsing

3. **curl Client** (`client_curl.sh`):
   - Bash script using curl and jq
   - Demonstrates raw HTTP requests
   - No Python dependencies required

## Requirements

- Python 3.13+
- fastmcp
- httpx (included as fastmcp dependency)
