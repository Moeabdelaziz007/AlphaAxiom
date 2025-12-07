import json
from js import fetch, Headers

# Capital.com API URLs
CAPITAL_DEMO_URL = "https://demo-api-capital.backend-capital.com"
CAPITAL_LIVE_URL = "https://api-capital.backend-capital.com"

class CapitalConnector:
    """
    💰 Capital.com Connector for Axiom Antigravity
    Handles Demo/Live Forex & CFD Trading via Capital.com REST API
    
    Advantages over OANDA:
    - Easier signup (no complex KYC for demo)
    - Modern REST API
    - Supports Forex, Gold, Stocks, Indices
    """
    
    def __init__(self, env):
        self.env = env
        self.api_key = str(getattr(env, 'CAPITAL_API_KEY', ''))
        self.identifier = str(getattr(env, 'CAPITAL_EMAIL', ''))  # Login email
        self.password = str(getattr(env, 'CAPITAL_PASSWORD', ''))  # API custom password
        self.is_demo = str(getattr(env, 'CAPITAL_DEMO', 'true')).lower() == 'true'
        self.base_url = CAPITAL_DEMO_URL if self.is_demo else CAPITAL_LIVE_URL
        
        # Session tokens (will be populated after login)
        self.cst = None  # Client Security Token
        self.x_security_token = None  # Account Security Token

    async def _start_session(self):
        """Start a new session and get auth tokens"""
        try:
            headers = Headers.new({
                "X-CAP-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }.items())
            
            body = json.dumps({
                "identifier": self.identifier,
                "password": self.password,
                "encryptedPassword": False
            })
            
            response = await fetch(
                f"{self.base_url}/api/v1/session",
                method="POST",
                headers=headers,
                body=body
            )
            
            if response.ok:
                # Extract security tokens from headers
                self.cst = response.headers.get("CST")
                self.x_security_token = response.headers.get("X-SECURITY-TOKEN")
                return True
            else:
                error_text = await response.text()
                print(f"Capital.com Session Error: {error_text}")
                return False
        except Exception as e:
            print(f"Capital.com Session Exception: {e}")
            return False

    def _get_auth_headers(self):
        """Get headers with auth tokens"""
        return Headers.new({
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst or "",
            "X-SECURITY-TOKEN": self.x_security_token or "",
            "Content-Type": "application/json"
        }.items())

    async def get_account_info(self):
        """Get account balance and equity"""
        try:
            if not self.cst:
                await self._start_session()
                
            if not self.cst:
                return {"error": "Failed to authenticate with Capital.com"}
            
            response = await fetch(
                f"{self.base_url}/api/v1/accounts",
                method="GET",
                headers=self._get_auth_headers()
            )
            
            if response.ok:
                data = json.loads(await response.text())
                accounts = data.get("accounts", [])
                if accounts:
                    acc = accounts[0]  # Use first account
                    balance = acc.get("balance", {})
                    return {
                        "balance": balance.get("balance", 0),
                        "equity": balance.get("balance", 0),  # They may use different fields
                        "available": balance.get("available", 0),
                        "currency": acc.get("currency", "USD"),
                        "account_id": acc.get("accountId", ""),
                        "source": "Capital.com Demo" if self.is_demo else "Capital.com Live"
                    }
            return {"error": "Failed to get account info"}
        except Exception as e:
            return {"error": str(e)}

    async def get_open_positions(self):
        """Get all open positions"""
        try:
            if not self.cst:
                await self._start_session()
                
            if not self.cst:
                return []
            
            response = await fetch(
                f"{self.base_url}/api/v1/positions",
                method="GET",
                headers=self._get_auth_headers()
            )
            
            if response.ok:
                data = json.loads(await response.text())
                positions = data.get("positions", [])
                
                clean_positions = []
                for p in positions:
                    position = p.get("position", {})
                    market = p.get("market", {})
                    clean_positions.append({
                        "symbol": market.get("epic", ""),
                        "side": position.get("direction", "").lower(),
                        "qty": position.get("size", 0),
                        "avg_entry_price": position.get("openLevel", 0),
                        "current_price": market.get("bid", 0),
                        "unrealized_pl": position.get("upl", 0),
                        "deal_id": position.get("dealId", "")
                    })
                return clean_positions
            return []
        except Exception as e:
            print(f"Capital.com Positions Error: {e}")
            return []

    async def create_position(self, epic, direction, size, stop_loss=None, take_profit=None):
        """
        Open a new position
        epic: Instrument ID (e.g., "EURUSD" or "GOLD")
        direction: "BUY" or "SELL"
        size: Position size
        """
        try:
            if not self.cst:
                await self._start_session()
                
            if not self.cst:
                return {"status": "error", "error": "Not authenticated"}
            
            order_body = {
                "epic": epic,
                "direction": direction.upper(),
                "size": size,
                "guaranteedStop": False,
                "trailingStop": False
            }
            
            if stop_loss:
                order_body["stopLevel"] = stop_loss
            if take_profit:
                order_body["profitLevel"] = take_profit
            
            response = await fetch(
                f"{self.base_url}/api/v1/positions",
                method="POST",
                headers=self._get_auth_headers(),
                body=json.dumps(order_body)
            )
            
            if response.ok:
                data = json.loads(await response.text())
                return {
                    "status": "success",
                    "deal_reference": data.get("dealReference", ""),
                    "message": "Position opened successfully"
                }
            else:
                error_data = json.loads(await response.text())
                return {
                    "status": "error",
                    "error": error_data.get("errorCode", "Unknown error")
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def close_position(self, deal_id):
        """Close an existing position by deal ID"""
        try:
            if not self.cst:
                await self._start_session()
                
            response = await fetch(
                f"{self.base_url}/api/v1/positions/{deal_id}",
                method="DELETE",
                headers=self._get_auth_headers()
            )
            
            if response.ok:
                return {"status": "success", "message": "Position closed"}
            else:
                return {"status": "error", "error": "Failed to close position"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_market_prices(self, epic):
        """Get current price for an instrument"""
        try:
            if not self.cst:
                await self._start_session()
            
            response = await fetch(
                f"{self.base_url}/api/v1/markets/{epic}",
                method="GET",
                headers=self._get_auth_headers()
            )
            
            if response.ok:
                data = json.loads(await response.text())
                snapshot = data.get("snapshot", {})
                return {
                    "epic": epic,
                    "bid": snapshot.get("bid", 0),
                    "offer": snapshot.get("offer", 0),
                    "high": snapshot.get("high", 0),
                    "low": snapshot.get("low", 0),
                    "change": snapshot.get("percentageChange", 0)
                }
            return {"error": "Failed to get prices"}
        except Exception as e:
            return {"error": str(e)}

    async def search_markets(self, search_term):
        """Search for available markets/instruments"""
        try:
            if not self.cst:
                await self._start_session()
            
            response = await fetch(
                f"{self.base_url}/api/v1/markets?searchTerm={search_term}",
                method="GET",
                headers=self._get_auth_headers()
            )
            
            if response.ok:
                data = json.loads(await response.text())
                markets = data.get("markets", [])
                return [{"epic": m.get("epic"), "name": m.get("instrumentName")} for m in markets[:10]]
            return []
        except:
            return []
