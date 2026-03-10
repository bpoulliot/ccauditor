#!/bin/sh
set -e

echo "Waiting for infrastructure services..."
python /app/scripts/wait_for_dependencies.py

echo "Starting Prometheus metrics server..."
python -c "from app.observability.metrics_server import start_http_server; start_http_server(8000)" &

echo "Starting Streamlit..."
exec python -m streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0