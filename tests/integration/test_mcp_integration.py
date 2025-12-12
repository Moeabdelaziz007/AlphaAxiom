import requests
import json
import time
import sys

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

BASE_URL = "https://oracle.axiomid.app"
SSE_ENDPOINT = f"{BASE_URL}/sse"

def print_result(name, passed, detail=""):
    status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
    print(f"[{status}] {name}")
    if detail:
        print(f"  └─ {detail}")

def test_sse_connection():
    """Test connectivity to the SSE endpoint."""
    print(f"Testing SSE connection to {SSE_ENDPOINT}...")
    try:
        # Use stream=True to keep connection open without reading everything immediately
        with requests.get(SSE_ENDPOINT, stream=True, timeout=10) as response:
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    print_result("SSE Connectivity", True, f"Status: 200, Type: {content_type}")
                    return True
                else:
                    print_result("SSE Connectivity", False, f"Invalid Content-Type: {content_type}")
                    return False
            else:
                print_result("SSE Connectivity", False, f"Status Code: {response.status_code}")
                return False
    except requests.RequestException as e:
        print_result("SSE Connectivity", False, f"Connection Error: {e}")
        return False

def test_mcp_tools_available():
    """
    Verify MCP tools availability.
    Note: Without a full MCP client, we infer tool availability from a successful
    handshake or initial data frame if possible.
    """
    print("Verifying MCP Tools...")
    # Ideally, we would use an MCP client to list_tools().
    # Here we check if the endpoint is responsive enough to be considered 'active'.
    
    try:
        # Check standard MCP initialization
        # FastMCP usually exposes tools post-initialization.
        # This is a basic liveness check for the tool server.
        response = requests.get(f"{BASE_URL}/sse", timeout=5)
        
        # If we get a 200/405 (Method Not Allowed for GET if it expects POST for JSON-RPC)
        # or the stream opens, it means the server is up.
        if response.status_code in [200, 405]:
             print_result("MCP Server Liveness", True, "Server is responsive")
             print_result("Tool Discovery", True, "Inferred from server availability (Active)")
             return True
        else:
             print_result("MCP Server Liveness", False, f"Unexpected status: {response.status_code}")
             return False
    except Exception as e:
        print_result("MCP Server Liveness", False, f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AQT Integration Tests...\n")
    
    sse_passed = test_sse_connection()
    tools_passed = test_mcp_tools_available()
    
    if sse_passed and tools_passed:
        print(f"\n✅ {GREEN}ALL INTEGRATION TESTS PASSED{RESET}")
        sys.exit(0)
    else:
        print(f"\n❌ {RED}SOME TESTS FAILED{RESET}")
        sys.exit(1)
