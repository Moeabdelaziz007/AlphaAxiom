"""
Test script for Money Machine IPC communication
Run with: python test_ipc.py
"""

import asyncio
import json
import socket


async def test_ipc_connection():
    """Test IPC connection to Python trading engine"""
    
    print("🔌 Testing IPC Connection to Money Machine Engine...")
    print("-" * 50)
    
    host = "127.0.0.1"
    port = 19284
    
    # Test 1: Simple ping
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        # Send PING command
        command = json.dumps({"command": "PING", "payload": {}}) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        # Read response
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"✅ PING Response: {result}")
        
        writer.close()
        await writer.wait_closed()
        
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the Python engine running?")
        print("   Start it with: python src-python/main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get Status
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        command = json.dumps({"command": "GET_STATUS", "payload": {}}) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"✅ GET_STATUS Response: {result}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Get Portfolio
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        command = json.dumps({"command": "GET_PORTFOLIO", "payload": {}}) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"✅ GET_PORTFOLIO Response: {result}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("-" * 50)
    print("🎉 All IPC tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_ipc_connection())
