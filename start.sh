#!/bin/bash
PORT=${PORT:-8000}
uvicorn api.index:app --host 0.0.0.0 --port $PORT