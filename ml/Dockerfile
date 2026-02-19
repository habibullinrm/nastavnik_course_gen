FROM python:3.11-slim

WORKDIR /app

# Set PYTHONPATH to include parent directory
ENV PYTHONPATH=/app:$PYTHONPATH \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for imports to work
RUN ln -s /app /app/ml

# Copy only dependency manifest first — this layer is cached unless pyproject.toml changes
COPY pyproject.toml ./
# Stub src/__init__.py so setuptools finds the package and can create the editable install;
# actual source code is copied in the next layer (COPY . . overwrites the stub)
RUN mkdir -p src && touch src/__init__.py && \
    pip install setuptools>=68.0 && \
    pip install --no-build-isolation -e .[dev]

# Copy actual source code (overwrites the stub src/__init__.py)
COPY . .

# Expose port
EXPOSE 8001

# Start server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
