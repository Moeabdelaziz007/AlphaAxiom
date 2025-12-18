#!/bin/bash
# Generate Ed25519 signing keys for Tauri auto-updater
# Run this ONCE locally, then add to GitHub Secrets

echo "🔐 Generating Ed25519 signing keys for Money Machine..."
echo ""

# Generate keys with password
npx @tauri-apps/cli signer generate -w ~/.tauri/money-machine.key

echo ""
echo "✅ Keys generated!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the PUBLIC KEY above and paste into:"
echo "   src-tauri/tauri.conf.json → plugins.updater.pubkey"
echo ""
echo "2. Add these GitHub Secrets (Settings → Secrets → Actions):"
echo "   TAURI_SIGNING_PRIVATE_KEY = contents of ~/.tauri/money-machine.key"
echo "   TAURI_SIGNING_PRIVATE_KEY_PASSWORD = password you entered"
echo ""
echo "🔒 NEVER commit the private key to git!"
