"""
Simple FIX 4.4 Client
Designed for stateless order placement in serverless environments.
"""

import asyncio
import datetime
import ssl
from typing import Dict, Optional, Tuple

# SOH character
SOH = "\x01"

class SimpleFixClient:
    """
    Simple FIX 4.4 Client for stateless order placement.

    Features:
    - Stateless execution (Connect -> Logon -> Trade -> Logout)
    - SSL support
    - Basic message parsing
    """

    def __init__(self, host: str, port: int, sender_id: str, target_id: str,
                 username: str = None, password: str = None, ssl_enabled: bool = True):
        self.host = host
        self.port = port
        self.sender_id = sender_id
        self.target_id = target_id
        self.username = username
        self.password = password
        self.ssl_enabled = ssl_enabled
        self.seq_num = 1
        self.reader = None
        self.writer = None
        self.connected = False

        # Buffer for incoming data
        self.buffer = b""

    async def connect(self):
        """Establish TCP connection with SSL if enabled."""
        if self.connected:
            return

        try:
            if self.ssl_enabled:
                ssl_ctx = ssl.create_default_context()
                # Allow self-signed certs if needed, but for brokers usually strictly valid
                # ssl_ctx.check_hostname = False
                # ssl_ctx.verify_mode = ssl.CERT_NONE
            else:
                ssl_ctx = None

            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port, ssl=ssl_ctx
            )
            self.connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to FIX server {self.host}:{self.port}: {str(e)}")

    async def disconnect(self):
        """Close connection."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
        self.connected = False
        self.reader = None
        self.writer = None

    def _generate_msg_header(self, msg_type: str) -> str:
        """Generate standard header."""
        t = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
        header = (
            f"35={msg_type}{SOH}"
            f"49={self.sender_id}{SOH}"
            f"56={self.target_id}{SOH}"
            f"34={self.seq_num}{SOH}"
            f"52={t}{SOH}"
        )
        self.seq_num += 1
        return header

    def _calculate_checksum(self, msg: str) -> str:
        """Calculate FIX checksum."""
        # Checksum is sum of all bytes % 256
        # Message body includes SOH
        total = sum(msg.encode('ascii'))
        return f"{total % 256:03d}"

    def _build_message(self, msg_type: str, body_tags: str) -> str:
        """Build full FIX message."""
        # Construct body (header + custom tags)
        # Note: BodyLength (9) covers from 35 to before 10.

        # First construct partial body to measure length
        # Start with MsgType, Sender, Target, SeqNum, Time
        header_content = self._generate_msg_header(msg_type)
        content = header_content + body_tags

        length = len(content)

        # Prefix: 8=FIX.4.4|9=LENGTH|
        prefix = f"8=FIX.4.4{SOH}9={length}{SOH}"

        full_msg_without_checksum = prefix + content
        checksum = self._calculate_checksum(full_msg_without_checksum)

        return f"{full_msg_without_checksum}10={checksum}{SOH}"

    async def _send_message(self, msg: str):
        """Send message to socket."""
        if not self.writer:
            raise ConnectionError("Not connected")
        self.writer.write(msg.encode('ascii'))
        await self.writer.drain()

    async def _read_message(self) -> Dict[str, str]:
        """Read next valid FIX message."""
        if not self.reader:
            raise ConnectionError("Not connected")

        # Read until we find '8=FIX...' and ends with '10=...SOH'
        # Simple implementation: read chunk, split by SOH, parse
        # This is a basic blocking read for simplicity in one-shot flow

        while True:
            # Read a chunk
            try:
                chunk = await self.reader.read(4096)
            except Exception as e:
                raise ConnectionError(f"Read failed: {e}")

            if not chunk:
                raise ConnectionError("Connection closed by peer")

            self.buffer += chunk

            # Check if we have a full message
            # FIX message ends with 10=XXX<SOH>
            # Pattern matching might be complex, let's look for "10=...<SOH>"

            msg_end_marker = f"10=".encode('ascii')

            # Loop to extract multiple messages if stuck together
            while True:
                # Find start
                start_idx = self.buffer.find(b"8=FIX")
                if start_idx == -1:
                    # Keep last part just in case
                    if len(self.buffer) > 20:
                        self.buffer = self.buffer[-20:]
                    break

                # If start is not 0, discard garbage before
                if start_idx > 0:
                    self.buffer = self.buffer[start_idx:]
                    start_idx = 0

                # Find end of checksum 10=XXX<SOH>
                # It should be around len - 7
                # We need to find the SOH after 10=XXX

                # Search for 10=
                checksum_idx = self.buffer.find(b"\x0110=")
                if checksum_idx == -1:
                    # Maybe incomplete
                    break

                # Check for SOH after checksum (3 digits)
                # 10=XXX<SOH> is 7 chars. \x01 is 1 char.
                # So \x0110=XXX\x01
                end_of_msg = checksum_idx + 8 # +1 for \x01, +3 for 10=, +3 for checksum, +1 for SOH

                if len(self.buffer) >= end_of_msg:
                    raw_msg = self.buffer[:end_of_msg]
                    self.buffer = self.buffer[end_of_msg:]
                    return self._parse_message(raw_msg.decode('ascii'))
                else:
                    break

    def _parse_message(self, msg: str) -> Dict[str, str]:
        """Parse FIX string to dict."""
        data = {}
        # Remove trailing SOH if present to avoid empty split
        if msg.endswith(SOH):
            msg = msg[:-1]

        parts = msg.split(SOH)
        for part in parts:
            if '=' in part:
                tag, value = part.split('=', 1)
                data[tag] = value
        return data

    async def logon(self) -> bool:
        """Send Logon message (A)."""
        # Tags: 98=EncryptMethod(0), 108=HeartBtInt(30)
        # 141=Y (ResetSeqNumFlag) - Critical for stateless connections
        # Optional: 553=Username, 554=Password
        body = f"98=0{SOH}108=30{SOH}141=Y{SOH}"
        if self.username:
            body += f"553={self.username}{SOH}"
        if self.password:
            body += f"554={self.password}{SOH}"

        msg = self._build_message("A", body)
        await self._send_message(msg)

        # Wait for response
        response = await self._read_message()
        if response.get('35') == 'A':
            return True
        if response.get('35') == '5': # Logout/Reject
            return False
        return False

    async def place_market_order(self, symbol: str, side: str, quantity: float, cl_ord_id: str) -> Dict:
        """
        Place Market Order (NewOrderSingle - D).

        Args:
            symbol: Symbol (e.g. "EURUSD")
            side: "BUY" or "SELL"
            quantity: Amount
            cl_ord_id: Unique ID
        """
        # Mapping
        # Side: 1=Buy, 2=Sell
        side_code = '1' if side.upper() == 'BUY' else '2'

        # OrdType: 1=Market
        # TransactTime: UTC
        t = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]

        # Construct body
        # 11=ClOrdId, 55=Symbol, 54=Side, 60=TransactTime, 38=OrderQty, 40=OrdType(1)
        # Some brokers require TimeInForce(59)=3 (IOC) or 1 (GTC)
        # Let's assume GTC (1) or IOC (3). Market orders often IOC or FOK.
        # Pepperstone cTrader FIX might default to GTC for limit, but Market...
        # let's use 1 (Market) and 59=1 (GTC)

        body = (
            f"11={cl_ord_id}{SOH}"
            f"55={symbol}{SOH}"
            f"54={side_code}{SOH}"
            f"60={t}{SOH}"
            f"38={quantity}{SOH}"
            f"40=1{SOH}"
            f"59=1{SOH}"
        )

        msg = self._build_message("D", body)
        await self._send_message(msg)

        # Wait for ExecutionReport (8)
        # Note: Might receive PendingNew first, then New/Filled.
        # We wait for the first ExecutionReport

        while True:
            response = await self._read_message()
            msg_type = response.get('35')

            if msg_type == '8': # ExecutionReport
                # Check ExecType (150) or OrdStatus (39)
                # 0=New, 1=Partial, 2=Filled, 8=Rejected
                status = response.get('39')
                if status == '8': # Rejected
                    return {"status": "REJECTED", "reason": response.get('58', 'Unknown')}
                if status in ['0', '1', '2']: # New or Filled
                    return {
                        "status": "ACCEPTED",
                        "order_id": response.get('37'),
                        "price": response.get('6'), # AvgPx
                        "filled": response.get('14') # CumQty
                    }
            elif msg_type == '3': # Reject (Session level)
                return {"status": "ERROR", "reason": response.get('58', 'Session Reject')}
            elif msg_type == 'j': # BusinessReject
                return {"status": "ERROR", "reason": response.get('58', 'Business Reject')}

    async def logout(self):
        """Send Logout (5)."""
        msg = self._build_message("5", "")
        try:
            await self._send_message(msg)
            # Wait for logout response, but don't block forever
            await asyncio.wait_for(self._read_message(), timeout=2.0)
        except Exception:
            pass
