# ========================================
# 🔐 OAUTH UTILITY FUNCTIONS
# ========================================
# Helper functions for OAuth flows
# ========================================

import json
from js import fetch


async def exchange_oauth_code(auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    """
    Exchange OAuth authorization code for access token.
    
    Args:
        auth_code: Authorization code received from OAuth provider
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: Redirect URI used in initial request
    
    Returns:
        Dictionary with token response or error
    """
    try:
        # Prepare token request
        token_url = "https://api.coinbase.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
        # Make token request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = await fetch(
            token_url,
            method="POST",
            headers=headers,
            body="&".join([f"{k}={v}" for k, v in payload.items()])
        )
        
        response_text = await response.text()
        
        if response.status >= 400:
            return {
                "error": "Token exchange failed",
                "status": response.status,
                "message": response_text
            }
        
        return json.loads(response_text)
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "exception"
        }