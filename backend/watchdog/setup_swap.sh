#!/bin/bash
# Startup script for GCP e2-micro to prevent OOM kills

echo "🚀 Starting Watchdog Setup..."

# 1. Create 2GB Swap File if it doesn't exist
SWAPFILE=/swapfile
if [ ! -f "$SWAPFILE" ]; then
    echo "📦 Creating 2GB Swap File..."
    fallocate -l 2G $SWAPFILE
    chmod 600 $SWAPFILE
    mkswap $SWAPFILE
    swapon $SWAPFILE
    echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab
    echo "✅ Swap created successfully."
else
    echo "✅ Swap file already exists."
fi

# 2. Adjust Swappiness (Prever swap over killing processes)
sysctl vm.swappiness=20
echo "vm.swappiness=20" >> /etc/sysctl.conf

# 3. Install Dependencies for Watchdog Listener
# Assuming python3 and pip are installed on the image
echo "📦 Installing Python dependencies..."
pip3 install websockets requests

# 4. Start the Watchdog Listener (in background)
# Ensure the script exists before running
if [ -f "/app/backend/watchdog/market_listener.py" ]; then
    echo "🐶 Starting Market Listener..."
    nohup python3 /app/backend/watchdog/market_listener.py > /var/log/market_listener.log 2>&1 &
else
    echo "⚠️ market_listener.py not found at /app/backend/watchdog/market_listener.py"
fi

echo "✅ Watchdog Setup Complete."
