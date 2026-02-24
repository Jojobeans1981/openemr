FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY app/ app/
COPY ui/ ui/
COPY evals/ evals/
COPY data/ data/
COPY start.sh .

# Install Python dependencies
RUN pip install --no-cache-dir .

RUN chmod +x start.sh

# Expose ports (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000 8501

CMD ["./start.sh"]
