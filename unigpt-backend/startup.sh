#!/bin/bash
# Start the FastAPI app using Uvicorn
uvicorn api:app --host=0.0.0.0 --port=${PORT:-8000}

chmod +x startup.sh