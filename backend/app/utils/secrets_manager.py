
import os
from typing import Optional

class SecretsManager:
    _instance = None
    _gsm_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecretsManager, cls).__new__(cls)
        return cls._instance

    def _get_gsm_client(self):
        """Lazy initialization of Google Secret Manager Client"""
        if self._gsm_client is None:
            try:
                from google.cloud import secretmanager
                self._gsm_client = secretmanager.SecretManagerServiceClient()
            except ImportError:
                print("Warning: google-cloud-secret-manager not installed. GSM disabled.")
                self._gsm_client = None
            except Exception as e:
                print(f"Warning: Failed to initialize GSM client: {e}")
                self._gsm_client = None
        return self._gsm_client

    def get_secret(self, secret_id: str, default: Optional[str] = None, project_id: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a secret with Fallback logic:
        1. Try Google Secret Manager (if configured)
        2. Fallback to Environment Variables
        3. Return Default
        """

        # 1. Try Google Secret Manager
        # We need a project ID to use GSM. Usually set in env GOOGLE_CLOUD_PROJECT
        project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")

        if project_id:
            client = self._get_gsm_client()
            if client:
                try:
                    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                    response = client.access_secret_version(request={"name": name})
                    return response.payload.data.decode("UTF-8")
                except Exception:
                    # If secret not found or permission denied, fall through to env var
                    pass

        # 2. Fallback to Environment Variables
        env_val = os.getenv(secret_id.upper())
        if env_val:
            return env_val

        # 3. Return Default
        return default

# Global Instance
secrets = SecretsManager()
