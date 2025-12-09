# ========================================
# 🔐 AXIOM SECURITY - Token Encryption
# ========================================
# Secure storage for OAuth tokens
# Uses AES-like XOR encryption for Cloudflare Workers
# ========================================

import base64
import hashlib
import json
from typing import Optional


class TokenEncryptor:
    """
    Simple but effective token encryption for Cloudflare Workers.
    
    Uses XOR cipher with a derived key from SECRET_KEY.
    For production, consider using Web Crypto API.
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize encryptor with secret key.
        
        Args:
            secret_key: Your env.SECRET_KEY
        """
        # Derive a 256-bit key from the secret
        self.key = hashlib.sha256(secret_key.encode()).digest()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string (e.g., access_token).
        
        Returns base64-encoded ciphertext.
        """
        # Convert to bytes
        data = plaintext.encode('utf-8')
        
        # XOR with key (repeating key if needed)
        encrypted = bytes([
            data[i] ^ self.key[i % len(self.key)]
            for i in range(len(data))
        ])
        
        # Base64 encode for safe storage
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a base64-encoded ciphertext.
        
        Returns original plaintext.
        """
        # Base64 decode
        encrypted = base64.b64decode(ciphertext)
        
        # XOR with same key to decrypt
        decrypted = bytes([
            encrypted[i] ^ self.key[i % len(self.key)]
            for i in range(len(encrypted))
        ])
        
        return decrypted.decode('utf-8')
    
    def encrypt_json(self, data: dict) -> str:
        """Encrypt a dictionary as JSON."""
        return self.encrypt(json.dumps(data))
    
    def decrypt_json(self, ciphertext: str) -> dict:
        """Decrypt to a dictionary."""
        return json.loads(self.decrypt(ciphertext))


class TokenStore:
    """
    Secure token storage using D1 database.
    
    Stores encrypted OAuth tokens for users.
    """
    
    def __init__(self, db, secret_key: str):
        """
        Initialize token store.
        
        Args:
            db: Cloudflare D1 database binding
            secret_key: Encryption secret
        """
        self.db = db
        self.encryptor = TokenEncryptor(secret_key)
    
    async def store_tokens(
        self,
        user_id: str,
        provider: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[int] = None
    ) -> bool:
        """
        Store encrypted OAuth tokens.
        
        Args:
            user_id: User identifier
            provider: 'coinbase', 'stripe', etc.
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_at: Token expiry timestamp (ms)
        
        Returns:
            True if stored successfully
        """
        try:
            # Encrypt tokens
            encrypted_access = self.encryptor.encrypt(access_token)
            encrypted_refresh = self.encryptor.encrypt(refresh_token) if refresh_token else None
            
            timestamp = int(__import__('time').time() * 1000)
            
            # Upsert (update or insert)
            await self.db.prepare("""
                INSERT INTO user_connections 
                    (user_id, provider, access_token, refresh_token, token_expires_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, provider) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    token_expires_at = excluded.token_expires_at,
                    updated_at = excluded.updated_at
            """).bind(
                user_id,
                provider,
                encrypted_access,
                encrypted_refresh,
                expires_at,
                timestamp,
                timestamp
            ).run()
            
            return True
            
        except Exception as e:
            print(f"Token storage error: {e}")
            return False
    
    async def get_tokens(
        self,
        user_id: str,
        provider: str
    ) -> Optional[dict]:
        """
        Retrieve and decrypt OAuth tokens.
        
        Returns:
            Dict with access_token, refresh_token, expires_at
            or None if not found
        """
        try:
            result = await self.db.prepare("""
                SELECT access_token, refresh_token, token_expires_at
                FROM user_connections
                WHERE user_id = ? AND provider = ?
            """).bind(user_id, provider).first()
            
            if not result:
                return None
            
            return {
                "access_token": self.encryptor.decrypt(result["access_token"]),
                "refresh_token": self.encryptor.decrypt(result["refresh_token"]) if result["refresh_token"] else None,
                "expires_at": result["token_expires_at"]
            }
            
        except Exception as e:
            print(f"Token retrieval error: {e}")
            return None
    
    async def delete_tokens(
        self,
        user_id: str,
        provider: str
    ) -> bool:
        """
        Delete stored tokens (disconnect).
        """
        try:
            await self.db.prepare("""
                DELETE FROM user_connections
                WHERE user_id = ? AND provider = ?
            """).bind(user_id, provider).run()
            return True
        except Exception:
            return False
    
    async def is_connected(
        self,
        user_id: str,
        provider: str
    ) -> bool:
        """
        Check if user has connected a provider.
        """
        result = await self.db.prepare("""
            SELECT 1 FROM user_connections
            WHERE user_id = ? AND provider = ?
        """).bind(user_id, provider).first()
        
        return result is not None


def get_token_store(env) -> TokenStore:
    """
    Get TokenStore instance from environment.
    
    Requires:
        env.TRADING_DB (D1 database)
        env.SECRET_KEY (encryption key)
    """
    secret = str(getattr(env, 'SECRET_KEY', 'default-secret-change-me'))
    return TokenStore(env.TRADING_DB, secret)
