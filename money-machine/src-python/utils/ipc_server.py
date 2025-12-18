"""
TCP-based IPC server for Rust ↔ Python communication
"""

import asyncio
import json
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class IPCServer:
    """TCP server for inter-process communication with Tauri/Rust backend"""
    
    def __init__(self, command_handler: Callable, host: str = "127.0.0.1", port: int = 19284):
        self.host = host
        self.port = port
        self.command_handler = command_handler
        self.server = None
    
    async def start(self):
        """Start the TCP server"""
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        addr = self.server.sockets[0].getsockname()
        logger.info(f"IPC Server listening on {addr[0]}:{addr[1]}")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connection"""
        addr = writer.get_extra_info('peername')
        logger.debug(f"New connection from {addr}")
        
        try:
            # Read request (read until newline)
            data = await reader.readline()
            if not data:
                return
            
            request_str = data.decode('utf-8').strip()
            
            # Parse JSON
            try:
                request = json.loads(request_str)
            except json.JSONDecodeError as e:
                error_response = json.dumps({"error": f"Invalid JSON: {e}"})
                writer.write((error_response + "\n").encode('utf-8'))
                await writer.drain()
                return
            
            command = request.get('command', '')
            payload = request.get('payload', {})
            
            # Execute command handler
            result = await self.command_handler(command, payload)
            
            # Send response
            response = json.dumps(result)
            writer.write((response + "\n").encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            logger.error(f"IPC handler error: {e}")
            error_response = json.dumps({"error": str(e)})
            writer.write((error_response + "\n").encode('utf-8'))
            await writer.drain()
        
        finally:
            writer.close()
            await writer.wait_closed()
            logger.debug(f"Connection closed from {addr}")
    
    async def stop(self):
        """Stop the server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
