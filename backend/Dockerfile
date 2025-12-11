FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc is needed for some python packages
# curl is needed for healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run defaults to 8080 usually, but we expose 8000 here.
# Cloud Run sets PORT env var which Uvicorn should respect if we configured it,
# but here we hardcode 8000. In Cloud Run, we should route traffic to 8000 or change this.)
# For standard Cloud Run, it's better to read PORT env var.
# But keeping it simple as per existing setup, assuming user maps port or sets env.
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Run the application
# Removed --reload for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
