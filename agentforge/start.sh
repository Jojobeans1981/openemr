#!/bin/bash
# Start both FastAPI and Streamlit
# Railway provides $PORT for the public-facing service

API_PORT=8000
UI_PORT=${PORT:-8501}

# Start FastAPI backend in background
uvicorn app.main:app --host 0.0.0.0 --port $API_PORT &

# Wait for API to be ready
sleep 2

# Start Streamlit frontend on Railway's PORT
streamlit run ui/streamlit_app.py \
  --server.port $UI_PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
