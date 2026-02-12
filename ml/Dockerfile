FROM python:3.11-slim

WORKDIR /app

# Set PYTHONPATH to include parent directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy all files first
COPY . .

# Create symlink for imports to work
RUN ln -s /app /app/ml

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8001

# Start server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
