#!/bin/bash

# Simple MCP Client using curl
# Tests the Simple Tools Server with raw HTTP requests
# Requires: curl, jq

SERVER_URL="http://localhost:8000/mcp"
SESSION_ID=""
REQUEST_ID=1

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install with: brew install jq"
    exit 1
fi

echo "=================================================="
echo "Connected to Simple Tools Server via curl"
echo "=================================================="
echo ""

# Function to parse SSE response and extract JSON data
parse_sse() {
    # Extract the data line from SSE format: "data: {...}"
    echo "$1" | grep "^data: " | sed 's/^data: //'
}

# Function to extract body from HTTP response (after headers)
extract_body() {
    echo "$1" | tr -d '\r' | awk 'BEGIN{body=0} /^$/{body=1; next} body{print}'
}

# Function to make MCP request
# Returns: session_id (first line) and JSON response (remaining lines)
mcp_request() {
    local method=$1
    local params=$2

    # Build headers array
    local headers=()
    headers+=(-H "Content-Type: application/json")
    headers+=(-H "Accept: application/json, text/event-stream")

    # Add session ID if available
    if [ -n "$SESSION_ID" ]; then
        headers+=(-H "Mcp-Session-Id: $SESSION_ID")
    fi

    # Build JSON-RPC request
    local request=$(cat <<EOF
{
    "jsonrpc": "2.0",
    "id": $REQUEST_ID,
    "method": "$method",
    "params": $params
}
EOF
)

    # Make request and capture response with headers (-i includes headers)
    local response=$(curl -s -i -X POST "$SERVER_URL" \
        "${headers[@]}" \
        -d "$request")

    # Extract session ID from headers if present
    local new_session_id=$(echo "$response" | tr -d '\r' | grep -i "^mcp-session-id:" | sed 's/^mcp-session-id: //i' | tr -d ' ')

    # Parse SSE response and extract JSON
    local body=$(extract_body "$response")
    local json=$(parse_sse "$body")

    # Output: session_id on first line, json on second line
    echo "$new_session_id"
    echo "$json"

    # Increment request ID
    REQUEST_ID=$((REQUEST_ID + 1))
}

# Test 1: Initialize
echo -e "${BLUE}Initializing session...${NC}"
init_result=$(mcp_request "initialize" '{
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
    }
}')

# Extract session ID from first line and JSON from remaining lines
SESSION_ID=$(echo "$init_result" | head -1)
init_response=$(echo "$init_result" | tail -n +2)

server_name=$(echo "$init_response" | jq -r '.result.serverInfo.name')
server_version=$(echo "$init_response" | jq -r '.result.serverInfo.version')
echo -e "Server info: ${GREEN}$server_name v$server_version${NC}"
echo ""

# Test 2: List tools
echo -e "${BLUE}Available tools:${NC}"
tools_result=$(mcp_request "tools/list" '{}')
tools_response=$(echo "$tools_result" | tail -n +2)

# Parse and display tools using jq
echo "$tools_response" | jq -r '.result.tools[] | "  - \(.name)"'
echo ""

# Test 3: Generate UUID
echo -e "${YELLOW}Test 1: Generate UUID${NC}"
uuid_result=$(mcp_request "tools/call" '{
    "name": "generate_uuid",
    "arguments": {
        "version": 4
    }
}')
uuid_response=$(echo "$uuid_result" | tail -n +2)

uuid_text=$(echo "$uuid_response" | jq -r '.result.content[0].text')
echo -e "Result: ${GREEN}$uuid_text${NC}"
echo ""

# Test 4: Convert temperature
echo -e "${YELLOW}Test 2: Convert temperature (0°C to Fahrenheit)${NC}"
temp_result=$(mcp_request "tools/call" '{
    "name": "convert_temperature",
    "arguments": {
        "value": 0,
        "from_unit": "C",
        "to_unit": "F"
    }
}')
temp_response=$(echo "$temp_result" | tail -n +2)

temp_text=$(echo "$temp_response" | jq -r '.result.content[0].text')
echo -e "Result: ${GREEN}$temp_text${NC}"
echo ""

# Test 5: Text statistics
echo -e "${YELLOW}Test 3: Text statistics${NC}"
text_result=$(mcp_request "tools/call" '{
    "name": "text_statistics",
    "arguments": {
        "text": "Hello world!\nThis is a test.\nThree lines total."
    }
}')
text_response=$(echo "$text_result" | tail -n +2)

text_text=$(echo "$text_response" | jq -r '.result.content[0].text')
echo -e "Result: ${GREEN}$text_text${NC}"
echo ""

echo "=================================================="
echo "All tests completed successfully!"
echo "=================================================="
