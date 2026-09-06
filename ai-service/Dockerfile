FROM python:3.11-slim

WORKDIR /app

# System dependencies (for chromadb, sentence-transformers, paddle)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformer model to avoid cold-start latency
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/chroma_data /app/models

# Expose port
EXPOSE 8001

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
